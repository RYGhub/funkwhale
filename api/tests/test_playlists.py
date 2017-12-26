import json
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone

from funkwhale_api.playlists import models
from funkwhale_api.playlists.serializers import PlaylistSerializer



def test_can_create_playlist(factories):
    tracks = factories['music.Track'].create_batch(5)
    playlist = factories['playlists.Playlist']()

    previous = None
    for track in tracks:
        previous = playlist.add_track(track, previous=previous)

    playlist_tracks = list(playlist.playlist_tracks.all())

    previous = None
    for idx, track in enumerate(tracks):
        plt = playlist_tracks[idx]
        assert plt.position == idx
        assert plt.track == track
        if previous:
            assert playlist_tracks[idx + 1] == previous
        assert plt.playlist == playlist


def test_can_create_playlist_via_api(logged_in_client):
    url = reverse('api:v1:playlists-list')
    data = {
        'name': 'test',
    }

    response = logged_in_client.post(url, data)

    playlist = logged_in_client.user.playlists.latest('id')
    assert playlist.name == 'test'


def test_can_add_playlist_track_via_api(factories, logged_in_client):
    tracks = factories['music.Track'].create_batch(5)
    playlist = factories['playlists.Playlist'](user=logged_in_client.user)
    url = reverse('api:v1:playlist-tracks-list')
    data = {
        'playlist': playlist.pk,
        'track': tracks[0].pk
    }

    response = logged_in_client.post(url, data)
    plts = logged_in_client.user.playlists.latest('id').playlist_tracks.all()
    assert plts.first().track == tracks[0]
