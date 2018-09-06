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
        music_models.TrackFile.objects.filter(
            Q(audio_file__isnull=False)
            & (Q(accessed_date__lt=limit) | Q(accessed_date=None))
        )
        .local(False)
        .exclude(audio_file="")
        .only("audio_file", "id")
        .order_by("id")
    )
    for tf in candidates:
        tf.audio_file.delete()

    # we also delete orphaned files, if any
    storage = models.LibraryTrack._meta.get_field("audio_file").storage
    files = get_files(storage, "federation_cache/tracks")
    existing = music_models.TrackFile.objects.filter(audio_file__in=files)
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

    dirs, files = storage.listdir(os.path.join(*parts))
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

    try:
        routes.inbox.dispatch(
            activity.payload,
            context={
                "actor": activity.actor,
                "inbox_items": list(activity.inbox_items.local().select_related()),
            },
        )
    except Exception:
        activity.inbox_items.local().update(
            delivery_attempts=F("delivery_attempts") + 1,
            last_delivery_date=timezone.now(),
        )
        raise
    else:
        activity.inbox_items.local().update(
            delivery_attempts=F("delivery_attempts") + 1,
            last_delivery_date=timezone.now(),
            is_delivered=True,
        )


@celery.app.task(name="federation.dispatch_outbox")
@celery.require_instance(models.Activity.objects.select_related(), "activity")
def dispatch_outbox(activity):
    """
    Deliver a local activity to its recipients
    """
    inbox_items = activity.inbox_items.all().select_related("actor")
    local_recipients_items = [ii for ii in inbox_items if ii.actor.is_local]
    if local_recipients_items:
        dispatch_inbox.delay(activity_id=activity.pk)
    remote_recipients_items = [ii for ii in inbox_items if not ii.actor.is_local]

    shared_inbox_urls = {
        ii.actor.shared_inbox_url
        for ii in remote_recipients_items
        if ii.actor.shared_inbox_url
    }
    inbox_urls = {
        ii.actor.inbox_url
        for ii in remote_recipients_items
        if not ii.actor.shared_inbox_url
    }
    for url in shared_inbox_urls:
        deliver_to_remote_inbox.delay(activity_id=activity.pk, shared_inbox_url=url)

    for url in inbox_urls:
        deliver_to_remote_inbox.delay(activity_id=activity.pk, inbox_url=url)


@celery.app.task(
    name="federation.deliver_to_remote_inbox",
    autoretry_for=[RequestException],
    retry_backoff=30,
    max_retries=5,
)
@celery.require_instance(models.Activity.objects.select_related(), "activity")
def deliver_to_remote_inbox(activity, inbox_url=None, shared_inbox_url=None):
    url = inbox_url or shared_inbox_url
    actor = activity.actor
    inbox_items = activity.inbox_items.filter(is_delivered=False)
    if inbox_url:
        inbox_items = inbox_items.filter(actor__inbox_url=inbox_url)
    else:
        inbox_items = inbox_items.filter(actor__shared_inbox_url=shared_inbox_url)
    logger.info("Preparing activity delivery to %s", url)
    auth = signing.get_auth(actor.private_key, actor.private_key_id)
    try:
        response = session.get_session().post(
            auth=auth,
            json=activity.payload,
            url=url,
            timeout=5,
            verify=settings.EXTERNAL_REQUESTS_VERIFY_SSL,
            headers={"Content-Type": "application/activity+json"},
        )
        logger.debug("Remote answered with %s", response.status_code)
        response.raise_for_status()
    except Exception:
        inbox_items.update(
            last_delivery_date=timezone.now(),
            delivery_attempts=F("delivery_attempts") + 1,
        )
        raise
    else:
        inbox_items.update(last_delivery_date=timezone.now(), is_delivered=True)
