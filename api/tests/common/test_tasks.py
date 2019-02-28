import pytest

from funkwhale_api.common import serializers
from funkwhale_api.common import signals
from funkwhale_api.common import tasks


def test_apply_migration(factories, mocker):
    mutation = factories["common.Mutation"](payload={})
    apply = mocker.patch.object(mutation.__class__, "apply")
    tasks.apply_mutation(mutation_id=mutation.pk)

    apply.assert_called_once_with()


def test_broadcast_mutation_created(factories, mocker):
    mutation = factories["common.Mutation"](payload={})
    factories["common.Mutation"](payload={}, is_approved=True)
    group_send = mocker.patch("funkwhale_api.common.channels.group_send")
    expected = serializers.APIMutationSerializer(mutation).data

    signals.mutation_created.send(sender=None, mutation=mutation)
    group_send.assert_called_with(
        "instance_activity",
        {
            "type": "event.send",
            "text": "",
            "data": {
                "type": "mutation.created",
                "mutation": expected,
                "pending_review_count": 1,
            },
        },
    )


def test_broadcast_mutation_updated(factories, mocker):
    mutation = factories["common.Mutation"](payload={}, is_approved=True)
    factories["common.Mutation"](payload={})
    group_send = mocker.patch("funkwhale_api.common.channels.group_send")
    expected = serializers.APIMutationSerializer(mutation).data

    signals.mutation_updated.send(
        sender=None, mutation=mutation, old_is_approved=False, new_is_approved=True
    )
    group_send.assert_called_with(
        "instance_activity",
        {
            "type": "event.send",
            "text": "",
            "data": {
                "type": "mutation.updated",
                "mutation": expected,
                "old_is_approved": False,
                "new_is_approved": True,
                "pending_review_count": 1,
            },
        },
    )


def test_cannot_apply_already_applied_migration(factories):
    mutation = factories["common.Mutation"](payload={}, is_applied=True)
    with pytest.raises(mutation.__class__.DoesNotExist):
        tasks.apply_mutation(mutation_id=mutation.pk)
