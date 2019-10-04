import datetime
import json
import logging
import os
import requests

from django.conf import settings
from django.db import transaction
from django.db.models import Q, F
from django.utils import timezone
from dynamic_preferences.registries import global_preferences_registry
from requests.exceptions import RequestException

from funkwhale_api.common import preferences
from funkwhale_api.common import session
from funkwhale_api.common import utils as common_utils
from funkwhale_api.music import models as music_models
from funkwhale_api.taskapp import celery

from . import actors
from . import jsonld
from . import keys
from . import models, signing
from . import serializers
from . import routes
from . import utils

logger = logging.getLogger(__name__)


@celery.app.task(name="federation.clean_music_cache")
def clean_music_cache():
    preferences = global_preferences_registry.manager()
    delay = preferences["federation__music_cache_duration"]
    if delay < 1:
        return  # cache clearing disabled
    limit = timezone.now() - datetime.timedelta(minutes=delay)

    candidates = (
        music_models.Upload.objects.filter(
            Q(audio_file__isnull=False)
            & (Q(accessed_date__lt=limit) | Q(accessed_date=None)),
            # library__actor__user=None,
        )
        .local(False)
        .exclude(audio_file="")
        .only("audio_file", "id")
        .order_by("id")
    )
    for upload in candidates:
        upload.audio_file.delete()

    # we also delete orphaned files, if any
    storage = models.LibraryTrack._meta.get_field("audio_file").storage
    files = get_files(storage, "federation_cache/tracks")
    existing = music_models.Upload.objects.filter(audio_file__in=files)
    missing = set(files) - set(existing.values_list("audio_file", flat=True))
    for m in missing:
        storage.delete(m)


def get_files(storage, *parts):
    """
    This is a recursive function that return all files available
    in a given directory using django's storage.
    """
    if not parts:
        raise ValueError("Missing path")
    try:
        dirs, files = storage.listdir(os.path.join(*parts))
    except FileNotFoundError:
        return []
    for dir in dirs:
        files += get_files(storage, *(list(parts) + [dir]))
    return [os.path.join(parts[-1], path) for path in files]


@celery.app.task(name="federation.dispatch_inbox")
@celery.require_instance(models.Activity.objects.select_related(), "activity")
def dispatch_inbox(activity, call_handlers=True):
    """
    Given an activity instance, triggers our internal delivery logic (follow
    creation, etc.)
    """

    routes.inbox.dispatch(
        activity.payload,
        context={
            "activity": activity,
            "actor": activity.actor,
            "inbox_items": activity.inbox_items.filter(is_read=False),
        },
        call_handlers=call_handlers,
    )


@celery.app.task(name="federation.dispatch_outbox")
@celery.require_instance(models.Activity.objects.select_related(), "activity")
def dispatch_outbox(activity):
    """
    Deliver a local activity to its recipients, both locally and remotely
    """
    inbox_items = activity.inbox_items.filter(is_read=False).select_related()

    if inbox_items.exists():
        call_handlers = activity.type in ["Follow"]
        dispatch_inbox.delay(activity_id=activity.pk, call_handlers=call_handlers)

    if not preferences.get("federation__enabled"):
        # federation is disabled, we only deliver to local recipients
        return

    deliveries = activity.deliveries.filter(is_delivered=False)

    for id in deliveries.values_list("pk", flat=True):
        deliver_to_remote.delay(delivery_id=id)


@celery.app.task(
    name="federation.deliver_to_remote_inbox",
    autoretry_for=[RequestException],
    retry_backoff=30,
    max_retries=5,
)
@celery.require_instance(
    models.Delivery.objects.filter(is_delivered=False).select_related(
        "activity__actor"
    ),
    "delivery",
)
def deliver_to_remote(delivery):

    if not preferences.get("federation__enabled"):
        # federation is disabled, we only deliver to local recipients
        return

    actor = delivery.activity.actor
    logger.info("Preparing activity delivery to %s", delivery.inbox_url)
    auth = signing.get_auth(actor.private_key, actor.private_key_id)
    try:
        response = session.get_session().post(
            auth=auth,
            json=delivery.activity.payload,
            url=delivery.inbox_url,
            timeout=5,
            verify=settings.EXTERNAL_REQUESTS_VERIFY_SSL,
            headers={"Content-Type": "application/activity+json"},
        )
        logger.debug("Remote answered with %s", response.status_code)
        response.raise_for_status()
    except Exception:
        delivery.last_attempt_date = timezone.now()
        delivery.attempts = F("attempts") + 1
        delivery.save(update_fields=["last_attempt_date", "attempts"])
        raise
    else:
        delivery.last_attempt_date = timezone.now()
        delivery.attempts = F("attempts") + 1
        delivery.is_delivered = True
        delivery.save(update_fields=["last_attempt_date", "attempts", "is_delivered"])


def fetch_nodeinfo(domain_name):
    s = session.get_session()
    wellknown_url = "https://{}/.well-known/nodeinfo".format(domain_name)
    response = s.get(
        url=wellknown_url, timeout=5, verify=settings.EXTERNAL_REQUESTS_VERIFY_SSL
    )
    response.raise_for_status()
    serializer = serializers.NodeInfoSerializer(data=response.json())
    serializer.is_valid(raise_exception=True)
    nodeinfo_url = None
    for link in serializer.validated_data["links"]:
        if link["rel"] == "http://nodeinfo.diaspora.software/ns/schema/2.0":
            nodeinfo_url = link["href"]
            break

    response = s.get(
        url=nodeinfo_url, timeout=5, verify=settings.EXTERNAL_REQUESTS_VERIFY_SSL
    )
    response.raise_for_status()
    return response.json()


@celery.app.task(name="federation.update_domain_nodeinfo")
@celery.require_instance(
    models.Domain.objects.external(), "domain", id_kwarg_name="domain_name"
)
def update_domain_nodeinfo(domain):
    now = timezone.now()
    try:
        nodeinfo = {"status": "ok", "payload": fetch_nodeinfo(domain.name)}
    except (
        requests.RequestException,
        serializers.serializers.ValidationError,
        ValueError,
    ) as e:
        nodeinfo = {"status": "error", "error": str(e)}

    service_actor_id = common_utils.recursive_getattr(
        nodeinfo, "payload.metadata.actorId", permissive=True
    )
    try:
        domain.service_actor = (
            utils.retrieve_ap_object(
                service_actor_id,
                actor=actors.get_service_actor(),
                queryset=models.Actor,
                serializer_class=serializers.ActorSerializer,
            )
            if service_actor_id
            else None
        )
    except (serializers.serializers.ValidationError, RequestException) as e:
        logger.warning(
            "Cannot fetch system actor for domain %s: %s", domain.name, str(e)
        )
    domain.nodeinfo_fetch_date = now
    domain.nodeinfo = nodeinfo
    domain.save(update_fields=["nodeinfo", "nodeinfo_fetch_date", "service_actor"])


@celery.app.task(name="federation.refresh_nodeinfo_known_nodes")
def refresh_nodeinfo_known_nodes():
    """
    Trigger a node info refresh on all nodes that weren't refreshed since
    settings.NODEINFO_REFRESH_DELAY
    """
    limit = timezone.now() - datetime.timedelta(seconds=settings.NODEINFO_REFRESH_DELAY)
    candidates = models.Domain.objects.external().exclude(
        nodeinfo_fetch_date__gte=limit
    )
    names = candidates.values_list("name", flat=True)
    logger.info("Launching periodic nodeinfo refresh on %s domains", len(names))
    for domain_name in names:
        update_domain_nodeinfo.delay(domain_name=domain_name)


def delete_qs(qs):
    label = qs.model._meta.label
    result = qs.delete()
    related = sum(result[1].values())

    logger.info(
        "Purged %s %s objects (and %s related entities)", result[0], label, related
    )


def handle_purge_actors(ids, only=[]):
    """
    Empty only means we purge everything
    Otherwise, we purge only the requested bits: media
    """
    # purge follows (received emitted)
    if not only:
        delete_qs(models.LibraryFollow.objects.filter(target__actor_id__in=ids))
        delete_qs(models.Follow.objects.filter(actor_id__in=ids))

    # purge audio content
    if not only or "media" in only:
        delete_qs(models.LibraryFollow.objects.filter(actor_id__in=ids))
        delete_qs(models.Follow.objects.filter(target_id__in=ids))
        delete_qs(music_models.Upload.objects.filter(library__actor_id__in=ids))
        delete_qs(music_models.Library.objects.filter(actor_id__in=ids))

    # purge remaining activities / deliveries
    if not only:
        delete_qs(models.InboxItem.objects.filter(actor_id__in=ids))
        delete_qs(models.Activity.objects.filter(actor_id__in=ids))


@celery.app.task(name="federation.purge_actors")
def purge_actors(ids=[], domains=[], only=[]):
    actors = models.Actor.objects.filter(
        Q(id__in=ids) | Q(domain_id__in=domains)
    ).order_by("id")
    found_ids = list(actors.values_list("id", flat=True))
    logger.info("Starting purging %s accounts", len(found_ids))
    handle_purge_actors(ids=found_ids, only=only)


@celery.app.task(name="federation.rotate_actor_key")
@celery.require_instance(models.Actor.objects.local(), "actor")
def rotate_actor_key(actor):
    pair = keys.get_key_pair()
    actor.private_key = pair[0].decode()
    actor.public_key = pair[1].decode()
    actor.save(update_fields=["private_key", "public_key"])


@celery.app.task(name="federation.fetch")
@transaction.atomic
@celery.require_instance(
    models.Fetch.objects.filter(status="pending").select_related("actor"), "fetch"
)
def fetch(fetch):
    actor = fetch.actor
    auth = signing.get_auth(actor.private_key, actor.private_key_id)

    def error(code, **kwargs):
        fetch.status = "errored"
        fetch.fetch_date = timezone.now()
        fetch.detail = {"error_code": code}
        fetch.detail.update(kwargs)
        fetch.save(update_fields=["fetch_date", "status", "detail"])

    try:
        response = session.get_session().get(
            auth=auth,
            url=fetch.url,
            timeout=5,
            verify=settings.EXTERNAL_REQUESTS_VERIFY_SSL,
            headers={"Content-Type": "application/activity+json"},
        )
        logger.debug("Remote answered with %s", response.status_code)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return error("http", status_code=e.response.status_code if e.response else None)
    except requests.exceptions.Timeout:
        return error("timeout")
    except requests.exceptions.ConnectionError as e:
        return error("connection", message=str(e))
    except requests.RequestException as e:
        return error("request", message=str(e))
    except Exception as e:
        return error("unhandled", message=str(e))

    try:
        payload = response.json()
    except json.decoder.JSONDecodeError:
        return error("invalid_json")

    try:
        doc = jsonld.expand(payload)
    except ValueError:
        return error("invalid_jsonld")

    try:
        type = doc.get("@type", [])[0]
    except IndexError:
        return error("missing_jsonld_type")
    try:
        serializer_class = fetch.serializers[type]
        model = serializer_class.Meta.model
    except (KeyError, AttributeError):
        fetch.status = "skipped"
        fetch.fetch_date = timezone.now()
        fetch.detail = {"reason": "unhandled_type", "type": type}
        return fetch.save(update_fields=["fetch_date", "status", "detail"])
    try:
        id = doc.get("@id")
    except IndexError:
        existing = None
    else:
        existing = model.objects.filter(fid=id).first()

    serializer = serializer_class(existing, data=payload)
    if not serializer.is_valid():
        return error("validation", validation_errors=serializer.errors)
    try:
        serializer.save()
    except Exception as e:
        error("save", message=str(e))
        raise

    fetch.status = "finished"
    fetch.fetch_date = timezone.now()
    return fetch.save(update_fields=["fetch_date", "status"])
