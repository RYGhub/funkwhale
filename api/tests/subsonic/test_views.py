import json
import pytest

from django.urls import reverse
from rest_framework.response import Response

from funkwhale_api.music import models as music_models
from funkwhale_api.music import views as music_views
from funkwhale_api.subsonic import renderers
from funkwhale_api.subsonic import serializers


def render_json(data):
    return json.loads(renderers.SubsonicJSONRenderer().render(data))


def test_render_content_json(db, api_client):
    url = reverse('api:subsonic-ping')
    response = api_client.get(url, {'f': 'json'})

    expected = {
        'status': 'ok',
        'version': '1.16.0'
    }
    assert response.status_code == 200
    assert json.loads(response.content) == render_json(expected)


@pytest.mark.parametrize('f', ['xml', 'json'])
def test_exception_wrong_credentials(f, db, api_client):
    url = reverse('api:subsonic-ping')
    response = api_client.get(url, {'f': f, 'u': 'yolo'})

    expected = {
        'status': 'failed',
        'error': {
            'code': 40,
            'message': 'Wrong username or password.'
        }
    }
    assert response.status_code == 200
    assert response.data == expected


@pytest.mark.parametrize('f', ['xml', 'json'])
def test_ping(f, db, api_client):
    url = reverse('api:subsonic-ping')
    response = api_client.get(url, {'f': f})

    expected = {
        'status': 'ok',
        'version': '1.16.0',
    }
    assert response.status_code == 200
    assert response.data == expected


@pytest.mark.parametrize('f', ['xml', 'json'])
def test_get_artists(f, db, logged_in_api_client, factories):
    url = reverse('api:subsonic-get-artists')
    assert url.endswith('getArtists') is True
    artists = factories['music.Artist'].create_batch(size=10)
    expected = {
        'artists': serializers.GetArtistsSerializer(
            music_models.Artist.objects.all()
        ).data
    }
    response = logged_in_api_client.get(url)

    assert response.status_code == 200
    assert response.data == expected


@pytest.mark.parametrize('f', ['xml', 'json'])
def test_get_artist(f, db, logged_in_api_client, factories):
    url = reverse('api:subsonic-get-artist')
    assert url.endswith('getArtist') is True
    artist = factories['music.Artist']()
    albums = factories['music.Album'].create_batch(size=3, artist=artist)
    expected = {
        'artist': serializers.GetArtistSerializer(artist).data
    }
    response = logged_in_api_client.get(url, {'id': artist.pk})

    assert response.status_code == 200
    assert response.data == expected


@pytest.mark.parametrize('f', ['xml', 'json'])
def test_get_album(f, db, logged_in_api_client, factories):
    url = reverse('api:subsonic-get-album')
    assert url.endswith('getAlbum') is True
    artist = factories['music.Artist']()
    album = factories['music.Album'](artist=artist)
    tracks = factories['music.Track'].create_batch(size=3, album=album)
    expected = {
        'album': serializers.GetAlbumSerializer(album).data
    }
    response = logged_in_api_client.get(url, {'f': f, 'id': album.pk})

    assert response.status_code == 200
    assert response.data == expected


@pytest.mark.parametrize('f', ['xml', 'json'])
def test_stream(f, db, logged_in_api_client, factories, mocker):
    url = reverse('api:subsonic-stream')
    mocked_serve = mocker.spy(
        music_views, 'handle_serve')
    assert url.endswith('stream') is True
    artist = factories['music.Artist']()
    album = factories['music.Album'](artist=artist)
    track = factories['music.Track'](album=album)
    tf = factories['music.TrackFile'](track=track)
    response = logged_in_api_client.get(url, {'f': f, 'id': track.pk})

    mocked_serve.assert_called_once_with(
        track_file=tf
    )
    assert response.status_code == 200
