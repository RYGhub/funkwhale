import io
import pytest

from funkwhale_api.music import views
from funkwhale_api.federation import actors


@pytest.mark.parametrize('param,expected', [
    ('true', 'full'),
    ('false', 'empty'),
])
def test_artist_view_filter_listenable(
        param, expected, factories, api_request):
    artists = {
        'empty': factories['music.Artist'](),
        'full': factories['music.TrackFile']().track.artist,
    }

    request = api_request.get('/', {'listenable': param})
    view = views.ArtistViewSet()
    view.action_map = {'get': 'list'}
    expected = [artists[expected]]
    view.request = view.initialize_request(request)
    queryset = view.filter_queryset(view.get_queryset())

    assert list(queryset) == expected


@pytest.mark.parametrize('param,expected', [
    ('true', 'full'),
    ('false', 'empty'),
])
def test_album_view_filter_listenable(
        param, expected, factories, api_request):
    artists = {
        'empty': factories['music.Album'](),
        'full': factories['music.TrackFile']().track.album,
    }

    request = api_request.get('/', {'listenable': param})
    view = views.AlbumViewSet()
    view.action_map = {'get': 'list'}
    expected = [artists[expected]]
    view.request = view.initialize_request(request)
    queryset = view.filter_queryset(view.get_queryset())

    assert list(queryset) == expected


def test_can_serve_track_file_as_remote_library(
        factories, authenticated_actor, settings, api_client):
    settings.PROTECT_AUDIO_FILES = True
    library_actor = actors.SYSTEM_ACTORS['library'].get_actor_instance()
    follow = factories['federation.Follow'](
        actor=authenticated_actor, target=library_actor)

    track_file = factories['music.TrackFile']()
    response = api_client.get(track_file.path)

    assert response.status_code == 200
    assert response['X-Accel-Redirect'] == "{}{}".format(
        settings.PROTECT_FILES_PATH,
        track_file.audio_file.url)


def test_can_serve_track_file_as_remote_library_deny_not_following(
        factories, authenticated_actor, settings, api_client):
    settings.PROTECT_AUDIO_FILES = True
    track_file = factories['music.TrackFile']()
    response = api_client.get(track_file.path)

    assert response.status_code == 403


def test_can_proxy_remote_track(
        factories, settings, api_client, r_mock):
    settings.PROTECT_AUDIO_FILES = False
    track_file = factories['music.TrackFile'](federation=True)

    r_mock.get(track_file.library_track.audio_url, body=io.StringIO('test'))
    response = api_client.get(track_file.path)

    assert response.status_code == 200
    assert list(response.streaming_content) == [b't', b'e', b's', b't']
    assert response['Content-Type'] == track_file.library_track.audio_mimetype
