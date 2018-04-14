import io
import pytest

from django.urls import reverse

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
        approved=True,
        actor=authenticated_actor,
        target=library_actor)

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

    r_mock.get(track_file.library_track.audio_url, body=io.BytesIO(b'test'))
    response = api_client.get(track_file.path)

    library_track = track_file.library_track
    library_track.refresh_from_db()
    assert response.status_code == 200
    assert response['X-Accel-Redirect'] == "{}{}".format(
        settings.PROTECT_FILES_PATH,
        library_track.audio_file.url)
    assert library_track.audio_file.read() == b'test'


def test_can_create_import_from_federation_tracks(
        factories, superuser_api_client, mocker):
    lts = factories['federation.LibraryTrack'].create_batch(size=5)
    mocker.patch('funkwhale_api.music.tasks.import_job_run')

    payload = {
        'library_tracks': [l.pk for l in lts]
    }
    url = reverse('api:v1:submit-federation')
    response = superuser_api_client.post(url, payload)

    assert response.status_code == 201
    batch = superuser_api_client.user.imports.latest('id')
    assert batch.jobs.count() == 5
    for i, job in enumerate(batch.jobs.all()):
        assert job.library_track == lts[i]
