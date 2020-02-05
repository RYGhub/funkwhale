from django.core.files.base import ContentFile
from django.utils.deconstruct import deconstructible

import bleach.sanitizer
import logging
import markdown
import os
import shutil
import uuid
import xml.etree.ElementTree as ET

from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

from django.conf import settings
from django import urls
from django.db import models, transaction

logger = logging.getLogger(__name__)


def rename_file(instance, field_name, new_name, allow_missing_file=False):
    field = getattr(instance, field_name)
    current_name, extension = os.path.splitext(field.name)

    new_name_with_extension = "{}{}".format(new_name, extension)
    try:
        shutil.move(field.path, new_name_with_extension)
    except FileNotFoundError:
        if not allow_missing_file:
            raise
        print("Skipped missing file", field.path)
    initial_path = os.path.dirname(field.name)
    field.name = os.path.join(initial_path, new_name_with_extension)
    instance.save()
    return new_name_with_extension


def on_commit(f, *args, **kwargs):
    return transaction.on_commit(lambda: f(*args, **kwargs))


def set_query_parameter(url, **kwargs):
    """Given a URL, set or replace a query parameter and return the
    modified URL.

    >>> set_query_parameter('http://example.com?foo=bar&biz=baz', 'foo', 'stuff')
    'http://example.com?foo=stuff&biz=baz'
    """
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)

    for param_name, param_value in kwargs.items():
        query_params[param_name] = [param_value]
    new_query_string = urlencode(query_params, doseq=True)

    return urlunsplit((scheme, netloc, path, new_query_string, fragment))


@deconstructible
class ChunkedPath(object):
    def __init__(self, root, preserve_file_name=True):
        self.root = root
        self.preserve_file_name = preserve_file_name

    def __call__(self, instance, filename):
        uid = str(uuid.uuid4())
        chunk_size = 2
        chunks = [uid[i : i + chunk_size] for i in range(0, len(uid), chunk_size)]
        if self.preserve_file_name:
            parts = chunks[:3] + [filename]
        else:
            ext = os.path.splitext(filename)[1][1:].lower()
            new_filename = "".join(chunks[3:]) + ".{}".format(ext)
            parts = chunks[:3] + [new_filename]
        return os.path.join(self.root, *parts)


def chunk_queryset(source_qs, chunk_size):
    """
    From https://github.com/peopledoc/django-chunkator/blob/master/chunkator/__init__.py
    """
    pk = None
    # In django 1.9, _fields is always present and `None` if 'values()' is used
    # In Django 1.8 and below, _fields will only be present if using `values()`
    has_fields = hasattr(source_qs, "_fields") and source_qs._fields
    if has_fields:
        if "pk" not in source_qs._fields:
            raise ValueError("The values() call must include the `pk` field")

    field = source_qs.model._meta.pk
    # set the correct field name:
    # for ForeignKeys, we want to use `model_id` field, and not `model`,
    # to bypass default ordering on related model
    order_by_field = field.attname

    source_qs = source_qs.order_by(order_by_field)
    queryset = source_qs
    while True:
        if pk:
            queryset = source_qs.filter(pk__gt=pk)
        page = queryset[:chunk_size]
        page = list(page)
        nb_items = len(page)

        if nb_items == 0:
            return

        last_item = page[-1]
        # source_qs._fields exists *and* is not none when using "values()"
        if has_fields:
            pk = last_item["pk"]
        else:
            pk = last_item.pk

        yield page

        if nb_items < chunk_size:
            return


def join_url(start, end):
    if end.startswith("http://") or end.startswith("https://"):
        # alread a full URL, joining makes no sense
        return end
    if start.endswith("/") and end.startswith("/"):
        return start + end[1:]

    if not start.endswith("/") and not end.startswith("/"):
        return start + "/" + end

    return start + end


def spa_reverse(name, args=[], kwargs={}):
    return urls.reverse(name, urlconf=settings.SPA_URLCONF, args=args, kwargs=kwargs)


def spa_resolve(path):
    return urls.resolve(path, urlconf=settings.SPA_URLCONF)


def parse_meta(html):
    # dirty but this is only for testing so we don't really care,
    # we convert the html string to xml so it can be parsed as xml
    html = '<?xml version="1.0"?>' + html
    tree = ET.fromstring(html)

    meta = [elem for elem in tree.iter() if elem.tag in ["meta", "link"]]

    return [dict([("tag", elem.tag)] + list(elem.items())) for elem in meta]


def order_for_search(qs, field):
    """
    When searching, it's often more useful to have short results first,
    this function will order the given qs based on the length of the given field
    """
    return qs.annotate(__size=models.functions.Length(field)).order_by("__size")


def recursive_getattr(obj, key, permissive=False):
    """
    Given a dictionary such as {'user': {'name': 'Bob'}} or and object and
    a dotted string such as user.name, returns 'Bob'.

    If the value is not present, returns None
    """
    v = obj
    for k in key.split("."):
        try:
            if hasattr(v, "get"):
                v = v.get(k)
            else:
                v = getattr(v, k)
        except (TypeError, AttributeError):
            if not permissive:
                raise
            return
        if v is None:
            return

    return v


def replace_prefix(queryset, field, old, new):
    """
    Given a queryset of objects and a field name, will find objects
    for which the field have the given value, and replace the old prefix by
    the new one.

    This is especially useful to find/update bad federation ids, to replace:

    http://wrongprotocolanddomain/path

    by

    https://goodprotocalanddomain/path

    on a whole table with a single query.
    """
    qs = queryset.filter(**{"{}__startswith".format(field): old})
    # we extract the part after the old prefix, and Concat it with our new prefix
    update = models.functions.Concat(
        models.Value(new),
        models.functions.Substr(field, len(old) + 1, output_field=models.CharField()),
    )
    return qs.update(**{field: update})


def concat_dicts(*dicts):
    n = {}
    for d in dicts:
        n.update(d)

    return n


def get_updated_fields(conf, data, obj):
    """
    Given a list of fields, a dict and an object, will return the dict keys/values
    that differ from the corresponding fields on the object.
    """
    final_conf = []
    for c in conf:
        if isinstance(c, str):
            final_conf.append((c, c))
        else:
            final_conf.append(c)

    final_data = {}

    for data_field, obj_field in final_conf:
        try:
            data_value = data[data_field]
        except KeyError:
            continue

        obj_value = getattr(obj, obj_field)
        if obj_value != data_value:
            final_data[obj_field] = data_value

    return final_data


def join_queries_or(left, right):
    if left:
        return left | right
    else:
        return right


def render_markdown(text):
    return markdown.markdown(text, extensions=["nl2br"])


HTMl_CLEANER = bleach.sanitizer.Cleaner(
    strip=True,
    tags=[
        "p",
        "a",
        "abbr",
        "acronym",
        "b",
        "blockquote",
        "code",
        "em",
        "i",
        "li",
        "ol",
        "strong",
        "ul",
    ],
)

HTML_LINKER = bleach.linkifier.Linker()


def clean_html(html):
    return HTMl_CLEANER.clean(html)


def render_html(text, content_type):
    rendered = render_markdown(text)
    if content_type == "text/html":
        rendered = text
    elif content_type == "text/markdown":
        rendered = render_markdown(text)
    else:
        rendered = render_markdown(text)
    rendered = HTML_LINKER.linkify(rendered)
    return clean_html(rendered).strip().replace("\n", "")


def render_plain_text(html):
    return bleach.clean(html, tags=[], strip=True)


@transaction.atomic
def attach_content(obj, field, content_data):
    from . import models

    existing = getattr(obj, "{}_id".format(field))

    if existing:
        getattr(obj, field).delete()
        setattr(obj, field, None)

    if not content_data:
        return

    content_obj = models.Content.objects.create(
        text=content_data["text"][: models.CONTENT_TEXT_MAX_LENGTH],
        content_type=content_data["content_type"],
    )
    setattr(obj, field, content_obj)
    obj.save(update_fields=[field])
    return content_obj


@transaction.atomic
def attach_file(obj, field, file_data, fetch=False):
    from . import models
    from . import tasks

    existing = getattr(obj, "{}_id".format(field))
    if existing:
        getattr(obj, field).delete()

    if not file_data:
        return

    extensions = {"image/jpeg": "jpg", "image/png": "png", "image/gif": "gif"}
    extension = extensions.get(file_data["mimetype"], "jpg")
    attachment = models.Attachment(mimetype=file_data["mimetype"])
    name_fields = ["uuid", "full_username", "pk"]
    name = [getattr(obj, field) for field in name_fields if getattr(obj, field, None)][
        0
    ]
    filename = "{}-{}.{}".format(field, name, extension)
    if "url" in file_data:
        attachment.url = file_data["url"]
    else:
        f = ContentFile(file_data["content"])
        attachment.file.save(filename, f, save=False)

    if not attachment.file and fetch:
        try:
            tasks.fetch_remote_attachment(attachment, filename=filename, save=False)
        except Exception as e:
            logger.warn("Cannot download attachment at url %s: %s", attachment.url, e)
            attachment = None

    if attachment:
        attachment.save()

    setattr(obj, field, attachment)
    obj.save(update_fields=[field])
    return attachment
