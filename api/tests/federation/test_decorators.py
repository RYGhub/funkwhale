from rest_framework import viewsets

from funkwhale_api.music import models as music_models

from funkwhale_api.federation import api_serializers
from funkwhale_api.federation import decorators
from funkwhale_api.federation import models
from funkwhale_api.federation import tasks


class V(viewsets.ModelViewSet):
    queryset = music_models.Track.objects.all()
    fetches = decorators.fetches_route()
    permission_classes = []


def test_fetches_route_create(factories, api_request, mocker):
    on_commit = mocker.patch("funkwhale_api.common.utils.on_commit")
    user = factories["users.User"]()
    actor = user.create_actor()
    track = factories["music.Track"]()
    view = V.as_view({"post": "fetches"})

    request = api_request.post("/", format="json")
    setattr(request, "user", user)
    setattr(request, "session", {})
    response = view(request, pk=track.pk)

    assert response.status_code == 201

    fetch = models.Fetch.objects.get_for_object(track).latest("id")
    on_commit.assert_called_once_with(tasks.fetch.delay, fetch_id=fetch.pk)

    assert fetch.url == track.fid
    assert fetch.object == track
    assert fetch.status == "pending"
    assert fetch.actor == actor

    expected = api_serializers.FetchSerializer(fetch).data
    assert response.data == expected


def test_fetches_route_create_local(factories, api_request, mocker, settings):
    user = factories["users.User"]()
    user.create_actor()
    track = factories["music.Track"](
        fid="https://{}/test".format(settings.FEDERATION_HOSTNAME)
    )
    view = V.as_view({"post": "fetches"})

    request = api_request.post("/", format="json")
    setattr(request, "user", user)
    setattr(request, "session", {})
    response = view(request, pk=track.pk)

    assert response.status_code == 400


def test_fetches_route_list(factories, api_request, mocker):
    user = factories["users.User"]()
    user.create_actor()
    track = factories["music.Track"]()
    fetches = [
        factories["federation.Fetch"](object=track),
        factories["federation.Fetch"](object=track),
    ]
    view = V.as_view({"get": "fetches"})

    request = api_request.get("/", format="json")
    setattr(request, "user", user)
    setattr(request, "session", {})
    expected = {
        "next": None,
        "previous": None,
        "count": 2,
        "results": api_serializers.FetchSerializer(reversed(fetches), many=True).data,
    }

    request = api_request.get("/")
    response = view(request, pk=track.pk)

    assert response.status_code == 200
    assert response.data == expected
