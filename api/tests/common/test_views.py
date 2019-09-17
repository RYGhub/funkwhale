import pytest
from django.urls import reverse

from funkwhale_api.common import serializers
from funkwhale_api.common import signals
from funkwhale_api.common import tasks
from funkwhale_api.common import throttling


def test_can_detail_mutation(logged_in_api_client, factories):
    mutation = factories["common.Mutation"](
        payload={}, target=factories["music.Artist"]()
    )
    url = reverse("api:v1:mutations-detail", kwargs={"uuid": mutation.uuid})

    response = logged_in_api_client.get(url)

    expected = serializers.APIMutationSerializer(mutation).data

    assert response.status_code == 200
    assert response.data == expected


def test_can_list_mutations(logged_in_api_client, factories):
    mutation = factories["common.Mutation"](
        payload={}, target=factories["music.Artist"]()
    )
    url = reverse("api:v1:mutations-list")

    response = logged_in_api_client.get(url)

    expected = serializers.APIMutationSerializer(mutation).data

    assert response.status_code == 200
    assert response.data["results"] == [expected]


def test_can_destroy_mutation_creator(logged_in_api_client, factories):
    actor = logged_in_api_client.user.create_actor()
    track = factories["music.Track"]()
    mutation = factories["common.Mutation"](
        target=track, type="update", payload={}, created_by=actor
    )
    url = reverse("api:v1:mutations-detail", kwargs={"uuid": mutation.uuid})

    response = logged_in_api_client.delete(url)

    assert response.status_code == 204


def test_can_destroy_mutation_not_creator(logged_in_api_client, factories):
    logged_in_api_client.user.create_actor()
    track = factories["music.Track"]()
    mutation = factories["common.Mutation"](type="update", target=track, payload={})
    url = reverse("api:v1:mutations-detail", kwargs={"uuid": mutation.uuid})

    response = logged_in_api_client.delete(url)

    assert response.status_code == 403

    mutation.refresh_from_db()


def test_can_destroy_mutation_has_perm(logged_in_api_client, factories, mocker):
    actor = logged_in_api_client.user.create_actor()
    track = factories["music.Track"]()
    mutation = factories["common.Mutation"](target=track, type="update", payload={})
    has_perm = mocker.patch(
        "funkwhale_api.common.mutations.registry.has_perm", return_value=True
    )
    url = reverse("api:v1:mutations-detail", kwargs={"uuid": mutation.uuid})

    response = logged_in_api_client.delete(url)

    assert response.status_code == 204
    has_perm.assert_called_once_with(
        obj=mutation.target, type=mutation.type, perm="approve", actor=actor
    )


@pytest.mark.parametrize("endpoint, expected", [("approve", True), ("reject", False)])
def test_can_approve_reject_mutation_with_perm(
    endpoint, expected, logged_in_api_client, factories, mocker
):
    on_commit = mocker.patch("funkwhale_api.common.utils.on_commit")
    actor = logged_in_api_client.user.create_actor()
    track = factories["music.Track"]()
    mutation = factories["common.Mutation"](target=track, type="update", payload={})
    has_perm = mocker.patch(
        "funkwhale_api.common.mutations.registry.has_perm", return_value=True
    )
    url = reverse(
        "api:v1:mutations-{}".format(endpoint), kwargs={"uuid": mutation.uuid}
    )

    response = logged_in_api_client.post(url)

    assert response.status_code == 200
    has_perm.assert_called_once_with(
        obj=mutation.target, type=mutation.type, perm="approve", actor=actor
    )

    if expected:
        on_commit.assert_any_call(tasks.apply_mutation.delay, mutation_id=mutation.id)
    mutation.refresh_from_db()

    assert mutation.is_approved == expected
    assert mutation.approved_by == actor

    on_commit.assert_any_call(
        signals.mutation_updated.send,
        mutation=mutation,
        sender=None,
        new_is_approved=expected,
        old_is_approved=None,
    )


@pytest.mark.parametrize("endpoint, expected", [("approve", True), ("reject", False)])
def test_cannot_approve_reject_applied_mutation(
    endpoint, expected, logged_in_api_client, factories, mocker
):
    on_commit = mocker.patch("funkwhale_api.common.utils.on_commit")
    logged_in_api_client.user.create_actor()
    track = factories["music.Track"]()
    mutation = factories["common.Mutation"](
        target=track, type="update", payload={}, is_applied=True
    )
    mocker.patch("funkwhale_api.common.mutations.registry.has_perm", return_value=True)
    url = reverse(
        "api:v1:mutations-{}".format(endpoint), kwargs={"uuid": mutation.uuid}
    )

    response = logged_in_api_client.post(url)

    assert response.status_code == 403
    on_commit.assert_not_called()

    mutation.refresh_from_db()

    assert mutation.is_approved is None
    assert mutation.approved_by is None


@pytest.mark.parametrize("endpoint, expected", [("approve", True), ("reject", False)])
def test_cannot_approve_reject_without_perm(
    endpoint, expected, logged_in_api_client, factories, mocker
):
    on_commit = mocker.patch("funkwhale_api.common.utils.on_commit")
    logged_in_api_client.user.create_actor()
    track = factories["music.Track"]()
    mutation = factories["common.Mutation"](target=track, type="update", payload={})
    mocker.patch("funkwhale_api.common.mutations.registry.has_perm", return_value=False)
    url = reverse(
        "api:v1:mutations-{}".format(endpoint), kwargs={"uuid": mutation.uuid}
    )

    response = logged_in_api_client.post(url)

    assert response.status_code == 403
    on_commit.assert_not_called()

    mutation.refresh_from_db()

    assert mutation.is_approved is None
    assert mutation.approved_by is None


def test_rate_limit(logged_in_api_client, now_time, settings, mocker):
    expected_ident = {"type": "authenticated", "id": logged_in_api_client.user.pk}

    expected = {
        "ident": expected_ident,
        "scopes": throttling.get_status(expected_ident, now_time),
        "enabled": settings.THROTTLING_ENABLED,
    }
    get_status = mocker.spy(throttling, "get_status")
    url = reverse("api:v1:rate-limit")
    response = logged_in_api_client.get(url)

    assert response.status_code == 200
    assert response.data == expected
    get_status.assert_called_once_with(expected_ident, now_time)
