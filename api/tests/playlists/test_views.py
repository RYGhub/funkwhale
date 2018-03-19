import json
import pytest

from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone

from funkwhale_api.playlists import models
from funkwhale_api.playlists import serializers


def test_can_create_playlist_via_api(logged_in_api_client):
    url = reverse('api:v1:playlists-list')
    data = {
        'name': 'test',
        'privacy_level': 'everyone'
    }

    response = logged_in_api_client.post(url, data)

    playlist = logged_in_api_client.user.playlists.latest('id')
    assert playlist.name == 'test'
    assert playlist.privacy_level == 'everyone'


def test_playlist_inherits_user_privacy(logged_in_api_client):
    url = reverse('api:v1:playlists-list')
    user = logged_in_api_client.user
    user.privacy_level = 'me'
    user.save()

    data = {
        'name': 'test',
    }

    response = logged_in_api_client.post(url, data)
    playlist = user.playlists.latest('id')
    assert playlist.privacy_level == user.privacy_level


def test_can_add_playlist_track_via_api(factories, logged_in_api_client):
    tracks = factories['music.Track'].create_batch(5)
    playlist = factories['playlists.Playlist'](user=logged_in_api_client.user)
    url = reverse('api:v1:playlist-tracks-list')
    data = {
        'playlist': playlist.pk,
        'track': tracks[0].pk
    }

    response = logged_in_api_client.post(url, data)
    assert response.status_code == 201
    plts = logged_in_api_client.user.playlists.latest('id').playlist_tracks.all()
    assert plts.first().track == tracks[0]


@pytest.mark.parametrize('name,method', [
    ('api:v1:playlist-tracks-list', 'post'),
    ('api:v1:playlists-list', 'post'),
])
def test_url_requires_login(name, method, factories, api_client):
    url = reverse(name)

    response = getattr(api_client, method)(url, {})

    assert response.status_code == 401


def test_only_can_add_track_on_own_playlist_via_api(
        factories, logged_in_api_client):
    track = factories['music.Track']()
    playlist = factories['playlists.Playlist']()
    url = reverse('api:v1:playlist-tracks-list')
    data = {
        'playlist': playlist.pk,
        'track': track.pk
    }

    response = logged_in_api_client.post(url, data)
    assert response.status_code == 400
    assert playlist.playlist_tracks.count() == 0


def test_deleting_plt_updates_indexes(
        mocker, factories, logged_in_api_client):
    remove = mocker.spy(models.Playlist, 'remove')
    track = factories['music.Track']()
    plt = factories['playlists.PlaylistTrack'](
        index=0,
        playlist__user=logged_in_api_client.user)
    url = reverse('api:v1:playlist-tracks-detail', kwargs={'pk': plt.pk})

    response = logged_in_api_client.delete(url)

    assert response.status_code == 204
    remove.assert_called_once_with(plt.playlist, 0)


@pytest.mark.parametrize('level', ['instance', 'me', 'followers'])
def test_playlist_privacy_respected_in_list_anon(level, factories, api_client):
    factories['playlists.Playlist'](privacy_level=level)
    url = reverse('api:v1:playlists-list')
    response = api_client.get(url)

    assert response.data['count'] == 0


@pytest.mark.parametrize('method', ['PUT', 'PATCH', 'DELETE'])
def test_only_owner_can_edit_playlist(method, factories, api_client):
    playlist = factories['playlists.Playlist']()
    url = reverse('api:v1:playlists-detail', kwargs={'pk': playlist.pk})
    response = api_client.get(url)

    assert response.status_code == 404


@pytest.mark.parametrize('method', ['PUT', 'PATCH', 'DELETE'])
def test_only_owner_can_edit_playlist_track(method, factories, api_client):
    plt = factories['playlists.PlaylistTrack']()
    url = reverse('api:v1:playlist-tracks-detail', kwargs={'pk': plt.pk})
    response = api_client.get(url)

    assert response.status_code == 404


@pytest.mark.parametrize('level', ['instance', 'me', 'followers'])
def test_playlist_track_privacy_respected_in_list_anon(
        level, factories, api_client):
    factories['playlists.PlaylistTrack'](playlist__privacy_level=level)
    url = reverse('api:v1:playlist-tracks-list')
    response = api_client.get(url)

    assert response.data['count'] == 0


@pytest.mark.parametrize('level', ['instance', 'me', 'followers'])
def test_can_list_tracks_from_playlist(
        level, factories, logged_in_api_client):
    plt = factories['playlists.PlaylistTrack'](
        playlist__user=logged_in_api_client.user)
    url = reverse('api:v1:playlists-tracks', kwargs={'pk': plt.playlist.pk})
    response = logged_in_api_client.get(url)
    serialized_plt = serializers.PlaylistTrackSerializer(plt).data

    assert response.data['count'] == 1
    assert response.data['result'][0] == serialized_plt
