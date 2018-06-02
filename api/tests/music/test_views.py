import io
import pytest

from django.urls import reverse
from django.utils import timezone

from funkwhale_api.music import serializers
from funkwhale_api.music import views
from funkwhale_api.federation import actors


@pytest.mark.parametrize('view,permissions,operator', [
    (views.ImportBatchViewSet, ['library', 'upload'], 'or'),
    (views.ImportJobViewSet, ['library', 'upload'], 'or'),
])
def test_permissions(assert_user_permission, view, permissions, operator):
    assert_user_permission(view, permissions, operator)


def test_artist_list_serializer(api_request, factories, logged_in_api_client):
    track = factories['music.Track']()
    artist = track.artist
    request = api_request.get('/')
    qs = artist.__class__.objects.with_albums()
    serializer = serializers.ArtistWithAlbumsSerializer(
        qs, many=True, context={'request': request})
    expected = {
        'count': 1,
        'next': None,
        'previous': None,
        'results': serializer.data
    }
    url = reverse('api:v1:artists-list')
    response = logged_in_api_client.get(url)

    assert response.status_code == 200
    assert response.data == expected


def test_album_list_serializer(api_request, factories, logged_in_api_client):
    track = factories['music.Track']()
    album = track.album
    request = api_request.get('/')
    qs = album.__class__.objects.all()
    serializer = serializers.AlbumSerializer(
        qs, many=True, context={'request': request})
    expected = {
        'count': 1,
        'next': None,
        'previous': None,
        'results': serializer.data
    }
    url = reverse('api:v1:albums-list')
    response = logged_in_api_client.get(url)

    assert response.status_code == 200
    assert response.data == expected


def test_track_list_serializer(api_request, factories, logged_in_api_client):
    track = factories['music.Track']()
    request = api_request.get('/')
    qs = track.__class__.objects.all()
    serializer = serializers.TrackSerializer(
        qs, many=True, context={'request': request})
    expected = {
        'count': 1,
        'next': None,
        'previous': None,
        'results': serializer.data
    }
    url = reverse('api:v1:tracks-list')
    response = logged_in_api_client.get(url)

    assert response.status_code == 200
    assert response.data == expected


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
        factories, authenticated_actor, api_client, settings, preferences):
    preferences['common__api_authentication_required'] = True
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
        factories, authenticated_actor, settings, api_client, preferences):
    preferences['common__api_authentication_required'] = True
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
        proxy,
        serve_path,
        expected,
        factories,
        api_client,
        preferences,
        settings):
    headers = {
        'apache2': 'X-Sendfile',
        'nginx': 'X-Accel-Redirect',
    }
    preferences['common__api_authentication_required'] = False
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
    ('apache2', '/host/music', '/host/music/hello/worldéà.mp3'),
    ('apache2', '/app/music', '/app/music/hello/worldéà.mp3'),
    ('nginx', '/host/music', '/_protected/music/hello/worldéà.mp3'),
    ('nginx', '/app/music', '/_protected/music/hello/worldéà.mp3'),
])
def test_serve_file_in_place_utf8(
        proxy,
        serve_path,
        expected,
        factories,
        api_client,
        settings,
        preferences):
    preferences['common__api_authentication_required'] = False
    settings.PROTECT_FILE_PATH = '/_protected/music'
    settings.REVERSE_PROXY_TYPE = proxy
    settings.MUSIC_DIRECTORY_PATH = '/app/music'
    settings.MUSIC_DIRECTORY_SERVE_PATH = serve_path
    path = views.get_file_path('/app/music/hello/worldéà.mp3')

    assert path == expected.encode('utf-8')


@pytest.mark.parametrize('proxy,serve_path,expected', [
    ('apache2', '/host/music', '/host/media/tracks/hello/world.mp3'),
    # apache with container not supported yet
    # ('apache2', '/app/music', '/app/music/tracks/hello/world.mp3'),
    ('nginx', '/host/music', '/_protected/media/tracks/hello/world.mp3'),
    ('nginx', '/app/music', '/_protected/media/tracks/hello/world.mp3'),
])
def test_serve_file_media(
        proxy,
        serve_path,
        expected,
        factories,
        api_client,
        settings,
        preferences):
    headers = {
        'apache2': 'X-Sendfile',
        'nginx': 'X-Accel-Redirect',
    }
    preferences['common__api_authentication_required'] = False
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
        factories, settings, api_client, r_mock, preferences):
    preferences['common__api_authentication_required'] = False
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


def test_serve_updates_access_date(
        factories, settings, api_client, preferences):
    preferences['common__api_authentication_required'] = False
    track_file = factories['music.TrackFile']()
    now = timezone.now()
    assert track_file.accessed_date is None

    response = api_client.get(track_file.path)
    track_file.refresh_from_db()

    assert response.status_code == 200
    assert track_file.accessed_date > now


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


def test_import_job_viewset_get_queryset_upload_filters_user(
        factories, logged_in_api_client):
    logged_in_api_client.user.permission_upload = True
    logged_in_api_client.user.save()

    job = factories['music.ImportJob']()
    url = reverse('api:v1:import-jobs-list')
    response = logged_in_api_client.get(url)

    assert response.data['count'] == 0


def test_import_batch_viewset_get_queryset_upload_filters_user(
        factories, logged_in_api_client):
    logged_in_api_client.user.permission_upload = True
    logged_in_api_client.user.save()

    job = factories['music.ImportBatch']()
    url = reverse('api:v1:import-batches-list')
    response = logged_in_api_client.get(url)

    assert response.data['count'] == 0
