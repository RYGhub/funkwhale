from django.db import transaction
from django.dispatch import receiver


from funkwhale_api.common import channels
from funkwhale_api.taskapp import celery

from . import models
from . import serializers
from . import signals


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
