import pytest

from django.urls import reverse

from funkwhale_api.federation import api_serializers
from funkwhale_api.federation import serializers
from funkwhale_api.federation import views


def test_user_can_list_their_library_follows(factories, logged_in_api_client):
    # followed by someont else
    factories["federation.LibraryFollow"]()
    follow = factories["federation.LibraryFollow"](
        actor__user=logged_in_api_client.user
    )
    url = reverse("api:v1:federation:library-follows-list")
    response = logged_in_api_client.get(url)

    assert response.data["count"] == 1
    assert response.data["results"][0]["uuid"] == str(follow.uuid)


def test_user_can_fetch_library_using_url(mocker, factories, logged_in_api_client):
    library = factories["music.Library"]()
    mocked_retrieve = mocker.patch(
        "funkwhale_api.federation.utils.retrieve_ap_object", return_value=library
    )
    url = reverse("api:v1:federation:libraries-fetch")
    response = logged_in_api_client.post(url, {"fid": library.fid})
    assert mocked_retrieve.call_count == 1
    args = mocked_retrieve.call_args
    assert args[0] == (library.fid,)
    assert args[1]["queryset"].model == views.MusicLibraryViewSet.queryset.model
    assert args[1]["serializer_class"] == serializers.LibrarySerializer
    assert response.status_code == 200
    assert response.data["results"] == [api_serializers.LibrarySerializer(library).data]


def test_user_can_schedule_library_scan(mocker, factories, logged_in_api_client):
    actor = logged_in_api_client.user.create_actor()
    library = factories["music.Library"](privacy_level="everyone")

    schedule_scan = mocker.patch(
        "funkwhale_api.music.models.Library.schedule_scan", return_value=True
    )
    url = reverse("api:v1:federation:libraries-scan", kwargs={"uuid": library.uuid})

    response = logged_in_api_client.post(url)

    assert response.status_code == 200

    schedule_scan.assert_called_once_with(actor=actor)


def test_can_follow_library(factories, logged_in_api_client, mocker):
    dispatch = mocker.patch("funkwhale_api.federation.routes.outbox.dispatch")
    actor = logged_in_api_client.user.create_actor()
    library = factories["music.Library"]()
    url = reverse("api:v1:federation:library-follows-list")
    response = logged_in_api_client.post(url, {"target": library.uuid})

    assert response.status_code == 201

    follow = library.received_follows.latest("id")

    assert follow.approved is None
    assert follow.actor == actor

    dispatch.assert_called_once_with({"type": "Follow"}, context={"follow": follow})


def test_can_undo_library_follow(factories, logged_in_api_client, mocker):
    dispatch = mocker.patch("funkwhale_api.federation.routes.outbox.dispatch")
    actor = logged_in_api_client.user.create_actor()
    follow = factories["federation.LibraryFollow"](actor=actor)
    delete = mocker.patch.object(follow.__class__, "delete")
    url = reverse(
        "api:v1:federation:library-follows-detail", kwargs={"uuid": follow.uuid}
    )
    response = logged_in_api_client.delete(url)

    assert response.status_code == 204

    delete.assert_called_once_with()
    dispatch.assert_called_once_with(
        {"type": "Undo", "object": {"type": "Follow"}}, context={"follow": follow}
    )


@pytest.mark.parametrize("action", ["accept", "reject"])
def test_user_cannot_edit_someone_else_library_follow(
    factories, logged_in_api_client, action
):
    logged_in_api_client.user.create_actor()
    follow = factories["federation.LibraryFollow"]()
    url = reverse(
        "api:v1:federation:library-follows-{}".format(action),
        kwargs={"uuid": follow.uuid},
    )
    response = logged_in_api_client.post(url)

    assert response.status_code == 404


@pytest.mark.parametrize("action,expected", [("accept", True), ("reject", False)])
def test_user_can_accept_or_reject_own_follows(
    factories, logged_in_api_client, action, expected, mocker
):
    mocked_dispatch = mocker.patch(
        "funkwhale_api.federation.activity.OutboxRouter.dispatch"
    )
    actor = logged_in_api_client.user.create_actor()
    follow = factories["federation.LibraryFollow"](target__actor=actor)
    url = reverse(
        "api:v1:federation:library-follows-{}".format(action),
        kwargs={"uuid": follow.uuid},
    )
    response = logged_in_api_client.post(url)

    assert response.status_code == 204

    follow.refresh_from_db()

    assert follow.approved is expected

    if action == "accept":
        mocked_dispatch.assert_called_once_with(
            {"type": "Accept"}, context={"follow": follow}
        )
    if action == "reject":
        mocked_dispatch.assert_not_called()


def test_user_can_list_inbox_items(factories, logged_in_api_client):
    actor = logged_in_api_client.user.create_actor()
    ii = factories["federation.InboxItem"](
        activity__type="Follow", actor=actor, type="to"
    )

    factories["federation.InboxItem"](activity__type="Follow", actor=actor, type="cc")
    factories["federation.InboxItem"](activity__type="Follow", type="to")

    url = reverse("api:v1:federation:inbox-list")

    response = logged_in_api_client.get(url)

    assert response.status_code == 200
    assert response.data == {
        "count": 1,
        "results": [api_serializers.InboxItemSerializer(ii).data],
        "next": None,
        "previous": None,
    }


def test_user_can_update_read_status_of_inbox_item(factories, logged_in_api_client):
    actor = logged_in_api_client.user.create_actor()
    ii = factories["federation.InboxItem"](
        activity__type="Follow", actor=actor, type="to"
    )

    url = reverse("api:v1:federation:inbox-detail", kwargs={"pk": ii.pk})

    response = logged_in_api_client.patch(url, {"is_read": True})
    assert response.status_code == 200

    ii.refresh_from_db()

    assert ii.is_read is True
