import datetime
import logging
import tempfile

from django.conf import settings
from django.core.files import File
from django.db import transaction
from django.dispatch import receiver
from django.utils import timezone

from funkwhale_api.common import channels
from funkwhale_api.taskapp import celery

from . import models
from . import serializers
from . import session
from . import signals

logger = logging.getLogger(__name__)


@celery.app.task(name="common.apply_mutation")
@transaction.atomic
@celery.require_instance(
    models.Mutation.objects.exclude(is_applied=True).select_for_update(), "mutation"
)
def apply_mutation(mutation):
    mutation.apply()


@receiver(signals.mutation_created)
def broadcast_mutation_created(mutation, **kwargs):
    group = "instance_activity"
    channels.group_send(
        group,
        {
            "type": "event.send",
            "text": "",
            "data": {
                "type": "mutation.created",
                "mutation": serializers.APIMutationSerializer(mutation).data,
                "pending_review_count": models.Mutation.objects.filter(
                    is_approved=None
                ).count(),
            },
        },
    )


@receiver(signals.mutation_updated)
def broadcast_mutation_update(mutation, old_is_approved, new_is_approved, **kwargs):
    group = "instance_activity"
    channels.group_send(
        group,
        {
            "type": "event.send",
            "text": "",
            "data": {
                "type": "mutation.updated",
                "mutation": serializers.APIMutationSerializer(mutation).data,
                "pending_review_count": models.Mutation.objects.filter(
                    is_approved=None
                ).count(),
                "old_is_approved": old_is_approved,
                "new_is_approved": new_is_approved,
            },
        },
    )


def fetch_remote_attachment(attachment, filename=None, save=True):
    if attachment.file:
        # already there, no need to fetch
        return

    s = session.get_session()
    attachment.last_fetch_date = timezone.now()
    with tempfile.TemporaryFile() as tf:
        with s.get(attachment.url, timeout=5, stream=True) as r:
            for chunk in r.iter_content(chunk_size=1024 * 100):
                tf.write(chunk)
            tf.seek(0)
            if not filename:
                filename = attachment.url.split("/")[-1]
                filename = filename[-50:]
            attachment.file.save(filename, File(tf), save=save)


@celery.app.task(name="common.prune_unattached_attachments")
def prune_unattached_attachments():
    limit = timezone.now() - datetime.timedelta(
        seconds=settings.ATTACHMENTS_UNATTACHED_PRUNE_DELAY
    )
    candidates = models.Attachment.objects.attached(False).filter(
        creation_date__lte=limit
    )

    total = candidates.count()
    logger.info("Deleting %s unattached attachments…", total)
    result = candidates.delete()
    logger.info("Deletion done: %s", result)
