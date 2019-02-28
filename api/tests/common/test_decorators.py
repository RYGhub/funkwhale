import pytest

from rest_framework import viewsets

from funkwhale_api.common import decorators
from funkwhale_api.common import models
from funkwhale_api.common import mutations
from funkwhale_api.common import serializers
from funkwhale_api.common import signals
from funkwhale_api.common import tasks
from funkwhale_api.music import models as music_models
from funkwhale_api.music import licenses


class V(viewsets.ModelViewSet):
    queryset = music_models.Track.objects.all()
    mutations = decorators.mutations_route(types=["update"])
    permission_classes = []


def test_mutations_route_list(factories, api_request):
    track = factories["music.Track"]()
    mutation = factories["common.Mutation"](target=track, type="update", payload="")
    factories["common.Mutation"](target=track, type="noop", payload="")

    view = V.as_view({"get": "mutations"})
    expected = {
        "next": None,
        "previous": None,
        "count": 1,
        "results": [serializers.APIMutationSerializer(mutation).data],
    }

    request = api_request.get("/")
    response = view(request, pk=track.pk)

    assert response.status_code == 200
    assert response.data == expected


@pytest.mark.parametrize("is_approved", [False, True])
def test_mutations_route_create_success(factories, api_request, is_approved, mocker):
    licenses.load(licenses.LICENSES)
    on_commit = mocker.patch("funkwhale_api.common.utils.on_commit")
    user = factories["users.User"](permission_library=True)
    actor = user.create_actor()
    track = factories["music.Track"](title="foo")
    view = V.as_view({"post": "mutations"})

    request = api_request.post(
        "/",
        {
            "type": "update",
            "payload": {"title": "bar", "unknown": "test", "license": "cc-by-nc-4.0"},
            "summary": "hello",
            "is_approved": is_approved,
        },
        format="json",
    )
    setattr(request, "user", user)
    setattr(request, "session", {})
    response = view(request, pk=track.pk)

    assert response.status_code == 201

    mutation = models.Mutation.objects.get_for_target(track).latest("id")

    assert mutation.type == "update"
    assert mutation.payload == {"title": "bar", "license": "cc-by-nc-4.0"}
    assert mutation.created_by == actor
    assert mutation.is_approved is is_approved
    assert mutation.is_applied is None
    assert mutation.target == track
    assert mutation.summary == "hello"

    if is_approved:
        on_commit.assert_any_call(tasks.apply_mutation.delay, mutation_id=mutation.pk)
    expected = serializers.APIMutationSerializer(mutation).data
    assert response.data == expected
    on_commit.assert_any_call(
        signals.mutation_created.send, mutation=mutation, sender=None
    )


def test_mutations_route_create_no_auth(factories, api_request):
    track = factories["music.Track"](title="foo")
    view = V.as_view({"post": "mutations"})

    request = api_request.post("/", {}, format="json")
    response = view(request, pk=track.pk)

    assert response.status_code == 401


@pytest.mark.parametrize("is_approved", [False, True])
def test_mutations_route_create_no_perm(factories, api_request, mocker, is_approved):
    track = factories["music.Track"](title="foo")
    view = V.as_view({"post": "mutations"})
    user = factories["users.User"]()
    actor = user.create_actor()
    has_perm = mocker.patch.object(mutations.registry, "has_perm", return_value=False)
    request = api_request.post(
        "/",
        {
            "type": "update",
            "payload": {"title": "bar", "unknown": "test"},
            "summary": "hello",
            "is_approved": is_approved,
        },
        format="json",
    )
    setattr(request, "user", user)
    setattr(request, "session", {})
    response = view(request, pk=track.pk)

    assert response.status_code == 403
    has_perm.assert_called_once_with(
        actor=actor,
        obj=track,
        type="update",
        perm="approve" if is_approved else "suggest",
    )
