import aiohttp
import asyncio
import functools

import pyld.jsonld
from django.conf import settings
import pyld.documentloader.requests
from rest_framework import serializers
from rest_framework.fields import empty
from . import contexts


def cached_contexts(loader):
    functools.wraps(loader)

    def load(url, *args, **kwargs):
        for cached in contexts.CONTEXTS:
            if url == cached["documentUrl"]:
                return cached
        return loader(url, *args, **kwargs)

    return load


def get_document_loader():
    loader = pyld.documentloader.requests.requests_document_loader(
        verify=settings.EXTERNAL_REQUESTS_VERIFY_SSL
    )
    return cached_contexts(loader)


def expand(doc, options=None, insert_fw_context=True):
    options = options or {}
    options.setdefault("documentLoader", get_document_loader())
    if isinstance(doc, str):
        doc = options["documentLoader"](doc)["document"]
    if insert_fw_context:
        fw = contexts.CONTEXTS_BY_ID["FW"]["documentUrl"]
        try:
            insert_context(fw, doc)
        except KeyError:
            # probably an already expanded document
            pass
    result = pyld.jsonld.expand(doc, options=options)
    try:
        # jsonld.expand returns a list, which is useless for us
        return result[0]
    except IndexError:
        raise ValueError("Impossible to expand this jsonld document")


def insert_context(ctx, doc):
    """
    In some situations, we may want to add a default context to an existing document.
    This function enable that (this will mutate the original document)
    """
    existing = doc["@context"]
    if isinstance(existing, list):
        if ctx not in existing:
            existing = existing[:]
            existing.append(ctx)
            doc["@context"] = existing
    else:
        doc["@context"] = [existing, ctx]
    return doc


def get_session():
    return aiohttp.ClientSession(raise_for_status=True)


async def fetch_json(url, session, cache=None, lock=None):
    async with session.get(url) as response:
        response.raise_for_status()
        return url, await response.json()


async def fetch_many(*ids, references=None):
    """
    Given a list of object ids, will fetch the remote
    representations for those objects, expand them
    and return a dictionnary with id as the key and expanded document as the values
    """
    ids = set(ids)
    results = references if references is not None else {}

    if not ids:
        return results

    async with get_session() as session:
        tasks = [fetch_json(url, session) for url in ids if url not in results]
        tasks_results = await asyncio.gather(*tasks)

    for url, payload in tasks_results:
        results[url] = payload

    return results


DEFAULT_PREPARE_CONFIG = {
    "type": {"property": "@type", "keep": "first"},
    "id": {"property": "@id"},
}


def dereference(value, references):
    """
    Given a payload and a dictonary containing ids and objects, will replace
    all the matching objects in the payload by the one in the references dictionary.
    """

    def replace(obj, id):
        try:
            matching = references[id]
        except KeyError:
            return
        # we clear the current dict, and replace its content by the matching obj
        obj.clear()
        obj.update(matching)

    if isinstance(value, dict):
        if "@id" in value:
            replace(value, value["@id"])
        else:
            for attr in value.values():
                dereference(attr, references)

    elif isinstance(value, list):
        # we loop on nested objects and trigger dereferencing
        for obj in value:
            dereference(obj, references)

    return value


def get_value(value, keep=None, attr=None):

    if keep == "first":
        value = value[0]
        if attr:
            value = value[attr]

    elif attr:
        value = [obj[attr] for obj in value if attr in obj]

    return value


def prepare_for_serializer(payload, config, fallbacks={}):
    """
    Json-ld payloads, as returned by expand are quite complex to handle, because
    every attr is basically a list of dictionnaries. To make code simpler,
    we use this function to clean the payload a little bit, base on the config object.

    Config is a dictionnary, with keys being serializer field names, and values
    being dictionaries describing how to handle this field.
    """
    final_payload = {}
    final_config = {}
    final_config.update(DEFAULT_PREPARE_CONFIG)
    final_config.update(config)
    for field, field_config in final_config.items():
        try:
            value = get_value(
                payload[field_config["property"]],
                keep=field_config.get("keep"),
                attr=field_config.get("attr"),
            )
        except (IndexError, KeyError):
            aliases = field_config.get("aliases", [])
            noop = object()
            value = noop
            if not aliases:
                continue

            for a in aliases:
                try:
                    value = get_value(
                        payload[a],
                        keep=field_config.get("keep"),
                        attr=field_config.get("attr"),
                    )
                except (IndexError, KeyError):
                    continue

                break

            if value is noop:
                continue

        final_payload[field] = value

    for key, choices in fallbacks.items():
        if key in final_payload:
            # initial attr was found, no need to rely on fallbacks
            continue

        for choice in choices:
            if choice not in final_payload:
                continue

            final_payload[key] = final_payload[choice]

    return final_payload


def get_ids(v):
    if isinstance(v, dict) and "@id" in v:
        yield v["@id"]

    if isinstance(v, list):
        for obj in v:
            yield from get_ids(obj)


def get_default_context():
    return ["https://www.w3.org/ns/activitystreams", "https://w3id.org/security/v1", {}]


def get_default_context_fw():
    return [
        "https://www.w3.org/ns/activitystreams",
        "https://w3id.org/security/v1",
        {},
        "https://funkwhale.audio/ns",
    ]


class JsonLdSerializer(serializers.Serializer):
    def run_validation(self, data=empty):
        if data and data is not empty and self.context.get("expand", True):
            try:
                data = expand(data)
            except ValueError:
                raise serializers.ValidationError(
                    "{} is not a valid jsonld document".format(data)
                )
            try:
                config = self.Meta.jsonld_mapping
            except AttributeError:
                config = {}
            try:
                fallbacks = self.Meta.jsonld_fallbacks
            except AttributeError:
                fallbacks = {}
            data = prepare_for_serializer(data, config, fallbacks=fallbacks)
            dereferenced_fields = [
                k
                for k, c in config.items()
                if k in data and c.get("dereference", False)
            ]
            dereferenced_ids = set()
            for field in dereferenced_fields:
                for i in get_ids(data[field]):
                    dereferenced_ids.add(i)

            if dereferenced_ids:
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                references = self.context.setdefault("references", {})
                loop.run_until_complete(
                    fetch_many(*dereferenced_ids, references=references)
                )
                data = dereference(data, references)
        return super().run_validation(data)


def first_attr(property, attr, aliases=[]):
    return {"property": property, "keep": "first", "attr": attr, "aliases": aliases}


def first_val(property, aliases=[]):
    return first_attr(property, "@value", aliases=aliases)


def first_id(property, aliases=[]):
    return first_attr(property, "@id", aliases=aliases)


def first_obj(property, aliases=[]):
    return {"property": property, "keep": "first", "aliases": aliases}


def raw(property, aliases=[]):
    return {"property": property, "aliases": aliases}
