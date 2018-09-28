import datetime
import logging
import os

from django.conf import settings
from django.db.models import Q, F
from django.utils import timezone
from dynamic_preferences.registries import global_preferences_registry
from requests.exceptions import RequestException

from funkwhale_api.common import session
from funkwhale_api.music import models as music_models
from funkwhale_api.taskapp import celery

from . import models, signing
from . import routes

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
def dispatch_inbox(activity):
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
    )


@celery.app.task(name="federation.dispatch_outbox")
@celery.require_instance(models.Activity.objects.select_related(), "activity")
def dispatch_outbox(activity):
    """
    Deliver a local activity to its recipients, both locally and remotely
    """
    inbox_items = activity.inbox_items.filter(is_read=False).select_related()
    deliveries = activity.deliveries.filter(is_delivered=False)

    if inbox_items.exists():
        dispatch_inbox.delay(activity_id=activity.pk)

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
