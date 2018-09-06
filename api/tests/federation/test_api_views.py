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


def test_user_can_scan_library_using_url(mocker, factories, logged_in_api_client):
    library = factories["music.Library"]()
    mocked_retrieve = mocker.patch(
        "funkwhale_api.federation.utils.retrieve", return_value=library
    )
    url = reverse("api:v1:federation:libraries-scan")
    response = logged_in_api_client.post(url, {"fid": library.fid})
    assert mocked_retrieve.call_count == 1
    args = mocked_retrieve.call_args
    assert args[0] == (library.fid,)
    assert args[1]["queryset"].model == views.MusicLibraryViewSet.queryset.model
    assert args[1]["serializer_class"] == serializers.LibrarySerializer
    assert response.status_code == 200
    assert response.data["results"] == [api_serializers.LibrarySerializer(library).data]


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
