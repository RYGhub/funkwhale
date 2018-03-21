import pytest

from rest_framework.views import APIView

from django.contrib.auth.models import AnonymousUser
from django.http import Http404

from funkwhale_api.common import permissions


def test_owner_permission_owner_field_ok(nodb_factories, api_request):
    playlist = nodb_factories['playlists.Playlist']()
    view = APIView.as_view()
    permission = permissions.OwnerPermission()
    request = api_request.get('/')
    setattr(request, 'user', playlist.user)
    check = permission.has_object_permission(request, view, playlist)

    assert check is True


def test_owner_permission_owner_field_not_ok(nodb_factories, api_request):
    playlist = nodb_factories['playlists.Playlist']()
    view = APIView.as_view()
    permission = permissions.OwnerPermission()
    request = api_request.get('/')
    setattr(request, 'user', AnonymousUser())

    with pytest.raises(Http404):
        permission.has_object_permission(request, view, playlist)


def test_owner_permission_read_only(nodb_factories, api_request):
    playlist = nodb_factories['playlists.Playlist']()
    view = APIView.as_view()
    setattr(view, 'owner_checks', ['write'])
    permission = permissions.OwnerPermission()
    request = api_request.get('/')
    setattr(request, 'user', AnonymousUser())
    check = permission.has_object_permission(request, view, playlist)

    assert check is True
