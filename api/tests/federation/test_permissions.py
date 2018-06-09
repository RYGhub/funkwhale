from rest_framework.views import APIView

from funkwhale_api.federation import actors
from funkwhale_api.federation import permissions


def test_library_follower(factories, api_request, anonymous_user, preferences):
    preferences["federation__music_needs_approval"] = True
    view = APIView.as_view()
    permission = permissions.LibraryFollower()
    request = api_request.get("/")
    setattr(request, "user", anonymous_user)
    check = permission.has_permission(request, view)

    assert check is False


def test_library_follower_actor_non_follower(
    factories, api_request, anonymous_user, preferences
):
    preferences["federation__music_needs_approval"] = True
    actor = factories["federation.Actor"]()
    view = APIView.as_view()
    permission = permissions.LibraryFollower()
    request = api_request.get("/")
    setattr(request, "user", anonymous_user)
    setattr(request, "actor", actor)
    check = permission.has_permission(request, view)

    assert check is False


def test_library_follower_actor_follower_not_approved(
    factories, api_request, anonymous_user, preferences
):
    preferences["federation__music_needs_approval"] = True
    library = actors.SYSTEM_ACTORS["library"].get_actor_instance()
    follow = factories["federation.Follow"](target=library, approved=False)
    view = APIView.as_view()
    permission = permissions.LibraryFollower()
    request = api_request.get("/")
    setattr(request, "user", anonymous_user)
    setattr(request, "actor", follow.actor)
    check = permission.has_permission(request, view)

    assert check is False


def test_library_follower_actor_follower(
    factories, api_request, anonymous_user, preferences
):
    preferences["federation__music_needs_approval"] = True
    library = actors.SYSTEM_ACTORS["library"].get_actor_instance()
    follow = factories["federation.Follow"](target=library, approved=True)
    view = APIView.as_view()
    permission = permissions.LibraryFollower()
    request = api_request.get("/")
    setattr(request, "user", anonymous_user)
    setattr(request, "actor", follow.actor)
    check = permission.has_permission(request, view)

    assert check is True
