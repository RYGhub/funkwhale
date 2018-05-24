from rest_framework.views import APIView

from funkwhale_api.federation import actors
from funkwhale_api.music import permissions


def test_list_permission_no_protect(preferences, anonymous_user, api_request):
    preferences['common__api_authentication_required'] = False
    view = APIView.as_view()
    permission = permissions.Listen()
    request = api_request.get('/')
    assert permission.has_permission(request, view) is True


def test_list_permission_protect_authenticated(
        factories, api_request, preferences):
    preferences['common__api_authentication_required'] = True
    user = factories['users.User']()
    view = APIView.as_view()
    permission = permissions.Listen()
    request = api_request.get('/')
    setattr(request, 'user', user)
    assert permission.has_permission(request, view) is True


def test_list_permission_protect_not_following_actor(
        factories, api_request, preferences):
    preferences['common__api_authentication_required'] = True
    actor = factories['federation.Actor']()
    view = APIView.as_view()
    permission = permissions.Listen()
    request = api_request.get('/')
    setattr(request, 'actor', actor)
    assert permission.has_permission(request, view) is False


def test_list_permission_protect_following_actor(
        factories, api_request, preferences):
    preferences['common__api_authentication_required'] = True
    library_actor = actors.SYSTEM_ACTORS['library'].get_actor_instance()
    follow = factories['federation.Follow'](
        approved=True, target=library_actor)
    view = APIView.as_view()
    permission = permissions.Listen()
    request = api_request.get('/')
    setattr(request, 'actor', follow.actor)

    assert permission.has_permission(request, view) is True


def test_list_permission_protect_following_actor_not_approved(
        factories, api_request, preferences):
    preferences['common__api_authentication_required'] = True
    library_actor = actors.SYSTEM_ACTORS['library'].get_actor_instance()
    follow = factories['federation.Follow'](
        approved=False, target=library_actor)
    view = APIView.as_view()
    permission = permissions.Listen()
    request = api_request.get('/')
    setattr(request, 'actor', follow.actor)

    assert permission.has_permission(request, view) is False
