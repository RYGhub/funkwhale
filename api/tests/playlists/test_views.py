import json
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone

from funkwhale_api.playlists import models
from funkwhale_api.playlists.serializers import PlaylistSerializer


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
    plts = logged_in_api_client.user.playlists.latest('id').playlist_tracks.all()
    assert plts.first().track == tracks[0]
