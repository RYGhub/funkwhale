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


@pytest.mark.parametrize('proxy,serve_path,expected', [
    ('apache2', '/host/music', '/host/music/hello/world.mp3'),
    ('apache2', '/app/music', '/app/music/hello/world.mp3'),
    ('nginx', '/host/music', '/_protected/music/hello/world.mp3'),
    ('nginx', '/app/music', '/_protected/music/hello/world.mp3'),
])
def test_serve_file_in_place(
        proxy, serve_path, expected, factories, api_client, settings):
    headers = {
        'apache2': 'X-Sendfile',
        'nginx': 'X-Accel-Redirect',
    }
    settings.PROTECT_AUDIO_FILES = False
    settings.PROTECT_FILE_PATH = '/_protected/music'
    settings.REVERSE_PROXY_TYPE = proxy
    settings.MUSIC_DIRECTORY_PATH = '/app/music'
    settings.MUSIC_DIRECTORY_SERVE_PATH = serve_path
    tf = factories['music.TrackFile'](
        in_place=True,
        source='file:///app/music/hello/world.mp3'
    )
    response = api_client.get(tf.path)

    assert response.status_code == 200
    assert response[headers[proxy]] == expected


@pytest.mark.parametrize('proxy,serve_path,expected', [
    ('apache2', '/host/music', '/host/media/tracks/hello/world.mp3'),
    # apache with container not supported yet
    # ('apache2', '/app/music', '/app/music/tracks/hello/world.mp3'),
    ('nginx', '/host/music', '/_protected/media/tracks/hello/world.mp3'),
    ('nginx', '/app/music', '/_protected/media/tracks/hello/world.mp3'),
])
def test_serve_file_media(
        proxy, serve_path, expected, factories, api_client, settings):
    headers = {
        'apache2': 'X-Sendfile',
        'nginx': 'X-Accel-Redirect',
    }
    settings.PROTECT_AUDIO_FILES = False
    settings.MEDIA_ROOT = '/host/media'
    settings.PROTECT_FILE_PATH = '/_protected/music'
    settings.REVERSE_PROXY_TYPE = proxy
    settings.MUSIC_DIRECTORY_PATH = '/app/music'
    settings.MUSIC_DIRECTORY_SERVE_PATH = serve_path

    tf = factories['music.TrackFile']()
    tf.__class__.objects.filter(pk=tf.pk).update(
        audio_file='tracks/hello/world.mp3')
    response = api_client.get(tf.path)

    assert response.status_code == 200
    assert response[headers[proxy]] == expected


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


def test_can_list_import_jobs(factories, superuser_api_client):
    job = factories['music.ImportJob']()
    url = reverse('api:v1:import-jobs-list')
    response = superuser_api_client.get(url)

    assert response.status_code == 200
    assert response.data['results'][0]['id'] == job.pk


def test_import_job_stats(factories, superuser_api_client):
    job1 = factories['music.ImportJob'](status='pending')
    job2 = factories['music.ImportJob'](status='errored')

    url = reverse('api:v1:import-jobs-stats')
    response = superuser_api_client.get(url)
    expected = {
        'errored': 1,
        'pending': 1,
        'finished': 0,
        'skipped': 0,
        'count': 2,
    }
    assert response.status_code == 200
    assert response.data == expected


def test_import_job_stats_filter(factories, superuser_api_client):
    job1 = factories['music.ImportJob'](status='pending')
    job2 = factories['music.ImportJob'](status='errored')

    url = reverse('api:v1:import-jobs-stats')
    response = superuser_api_client.get(url, {'batch': job1.batch.pk})
    expected = {
        'errored': 0,
        'pending': 1,
        'finished': 0,
        'skipped': 0,
        'count': 1,
    }
    assert response.status_code == 200
    assert response.data == expected


def test_import_job_run_via_api(factories, superuser_api_client, mocker):
    run = mocker.patch('funkwhale_api.music.tasks.import_job_run.delay')
    job1 = factories['music.ImportJob'](status='errored')
    job2 = factories['music.ImportJob'](status='pending')

    url = reverse('api:v1:import-jobs-run')
    response = superuser_api_client.post(url, {'jobs': [job2.pk, job1.pk]})

    job1.refresh_from_db()
    job2.refresh_from_db()
    assert response.status_code == 200
    assert response.data == {'jobs': [job1.pk, job2.pk]}
    assert job1.status == 'pending'
    assert job2.status == 'pending'

    run.assert_any_call(import_job_id=job1.pk)
    run.assert_any_call(import_job_id=job2.pk)


def test_import_batch_run_via_api(factories, superuser_api_client, mocker):
    run = mocker.patch('funkwhale_api.music.tasks.import_job_run.delay')

    batch = factories['music.ImportBatch']()
    job1 = factories['music.ImportJob'](batch=batch, status='errored')
    job2 = factories['music.ImportJob'](batch=batch, status='pending')

    url = reverse('api:v1:import-jobs-run')
    response = superuser_api_client.post(url, {'batches': [batch.pk]})

    job1.refresh_from_db()
    job2.refresh_from_db()
    assert response.status_code == 200
    assert job1.status == 'pending'
    assert job2.status == 'pending'

    run.assert_any_call(import_job_id=job1.pk)
    run.assert_any_call(import_job_id=job2.pk)


def test_import_batch_and_job_run_via_api(
        factories, superuser_api_client, mocker):
    run = mocker.patch('funkwhale_api.music.tasks.import_job_run.delay')

    batch = factories['music.ImportBatch']()
    job1 = factories['music.ImportJob'](batch=batch, status='errored')
    job2 = factories['music.ImportJob'](status='pending')

    url = reverse('api:v1:import-jobs-run')
    response = superuser_api_client.post(
        url, {'batches': [batch.pk], 'jobs': [job2.pk]})

    job1.refresh_from_db()
    job2.refresh_from_db()
    assert response.status_code == 200
    assert job1.status == 'pending'
    assert job2.status == 'pending'

    run.assert_any_call(import_job_id=job1.pk)
    run.assert_any_call(import_job_id=job2.pk)
