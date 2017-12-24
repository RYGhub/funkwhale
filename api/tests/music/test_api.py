import json
import pytest
from django.urls import reverse

from funkwhale_api.music import models
from funkwhale_api.musicbrainz import api
from funkwhale_api.music import serializers

from . import data as api_data


def test_can_submit_youtube_url_for_track_import(mocker, superuser_client):
    mocker.patch(
        'funkwhale_api.musicbrainz.api.artists.get',
        return_value=api_data.artists['get']['adhesive_wombat'])
    mocker.patch(
        'funkwhale_api.musicbrainz.api.releases.get',
        return_value=api_data.albums['get']['marsupial'])
    mocker.patch(
        'funkwhale_api.musicbrainz.api.recordings.get',
        return_value=api_data.tracks['get']['8bitadventures'])
    mocker.patch(
        'funkwhale_api.music.models.TrackFile.download_file',
        return_value=None)
    mbid = '9968a9d6-8d92-4051-8f76-674e157b6eed'
    video_id = 'tPEE9ZwTmy0'
    url = reverse('api:v1:submit-single')
    response = superuser_client.post(
        url,
        {'import_url': 'https://www.youtube.com/watch?v={0}'.format(video_id),
         'mbid': mbid})
    track = models.Track.objects.get(mbid=mbid)
    assert track.artist.name == 'Adhesive Wombat'
    assert track.album.title == 'Marsupial Madness'


def test_import_creates_an_import_with_correct_data(superuser_client, settings):
    mbid = '9968a9d6-8d92-4051-8f76-674e157b6eed'
    video_id = 'tPEE9ZwTmy0'
    url = reverse('api:v1:submit-single')
    settings.CELERY_ALWAYS_EAGER = False
    response = superuser_client.post(
        url,
        {'import_url': 'https://www.youtube.com/watch?v={0}'.format(video_id),
         'mbid': mbid})

    batch = models.ImportBatch.objects.latest('id')
    assert batch.jobs.count() == 1
    assert batch.submitted_by == superuser_client.user
    assert batch.status == 'pending'
    job = batch.jobs.first()
    assert str(job.mbid) == mbid
    assert job.status == 'pending'
    assert job.source == 'https://www.youtube.com/watch?v={0}'.format(video_id)


def test_can_import_whole_album(mocker, superuser_client, settings):
    mocker.patch(
        'funkwhale_api.musicbrainz.api.artists.get',
        return_value=api_data.artists['get']['soad'])
    mocker.patch(
        'funkwhale_api.musicbrainz.api.images.get_front',
        return_value=b'')
    mocker.patch(
        'funkwhale_api.musicbrainz.api.releases.get',
        return_value=api_data.albums['get_with_includes']['hypnotize'])
    payload = {
        'releaseId': '47ae093f-1607-49a3-be11-a15d335ccc94',
        'tracks': [
            {
            'mbid': '1968a9d6-8d92-4051-8f76-674e157b6eed',
            'source': 'https://www.youtube.com/watch?v=1111111111',
            },
            {
            'mbid': '2968a9d6-8d92-4051-8f76-674e157b6eed',
            'source': 'https://www.youtube.com/watch?v=2222222222',
            },
            {
            'mbid': '3968a9d6-8d92-4051-8f76-674e157b6eed',
            'source': 'https://www.youtube.com/watch?v=3333333333',
            },
        ]
    }
    url = reverse('api:v1:submit-album')
    settings.CELERY_ALWAYS_EAGER = False
    response = superuser_client.post(
        url, json.dumps(payload), content_type="application/json")

    batch = models.ImportBatch.objects.latest('id')
    assert batch.jobs.count() == 3
    assert batch.submitted_by == superuser_client.user
    assert batch.status == 'pending'

    album = models.Album.objects.latest('id')
    assert str(album.mbid) == '47ae093f-1607-49a3-be11-a15d335ccc94'
    medium_data = api_data.albums['get_with_includes']['hypnotize']['release']['medium-list'][0]
    assert int(medium_data['track-count']) == album.tracks.all().count()

    for track in medium_data['track-list']:
        instance = models.Track.objects.get(mbid=track['recording']['id'])
        assert instance.title == track['recording']['title']
        assert instance.position == int(track['position'])
        assert instance.title == track['recording']['title']

    for row in payload['tracks']:
        job = models.ImportJob.objects.get(mbid=row['mbid'])
        assert str(job.mbid) == row['mbid']
        assert job.status == 'pending'
        assert job.source == row['source']


def test_can_import_whole_artist(mocker, superuser_client, settings):
    mocker.patch(
        'funkwhale_api.musicbrainz.api.artists.get',
        return_value=api_data.artists['get']['soad'])
    mocker.patch(
        'funkwhale_api.musicbrainz.api.images.get_front',
        return_value=b'')
    mocker.patch(
        'funkwhale_api.musicbrainz.api.releases.get',
        return_value=api_data.albums['get_with_includes']['hypnotize'])
    payload = {
        'artistId': 'mbid',
        'albums': [
            {
                'releaseId': '47ae093f-1607-49a3-be11-a15d335ccc94',
                'tracks': [
                    {
                    'mbid': '1968a9d6-8d92-4051-8f76-674e157b6eed',
                    'source': 'https://www.youtube.com/watch?v=1111111111',
                    },
                    {
                    'mbid': '2968a9d6-8d92-4051-8f76-674e157b6eed',
                    'source': 'https://www.youtube.com/watch?v=2222222222',
                    },
                    {
                    'mbid': '3968a9d6-8d92-4051-8f76-674e157b6eed',
                    'source': 'https://www.youtube.com/watch?v=3333333333',
                    },
                ]
            }
        ]
    }
    url = reverse('api:v1:submit-artist')
    settings.CELERY_ALWAYS_EAGER = False
    response = superuser_client.post(
        url, json.dumps(payload), content_type="application/json")

    batch = models.ImportBatch.objects.latest('id')
    assert batch.jobs.count() == 3
    assert batch.submitted_by == superuser_client.user
    assert batch.status == 'pending'

    album = models.Album.objects.latest('id')
    assert str(album.mbid) == '47ae093f-1607-49a3-be11-a15d335ccc94'
    medium_data = api_data.albums['get_with_includes']['hypnotize']['release']['medium-list'][0]
    assert int(medium_data['track-count']) == album.tracks.all().count()

    for track in medium_data['track-list']:
        instance = models.Track.objects.get(mbid=track['recording']['id'])
        assert instance.title == track['recording']['title']
        assert instance.position == int(track['position'])
        assert instance.title == track['recording']['title']

    for row in payload['albums'][0]['tracks']:
        job = models.ImportJob.objects.get(mbid=row['mbid'])
        assert str(job.mbid) == row['mbid']
        assert job.status == 'pending'
        assert job.source == row['source']


def test_user_can_query_api_for_his_own_batches(client, factories):
    user1 = factories['users.SuperUser']()
    user2 = factories['users.SuperUser']()

    job = factories['music.ImportJob'](batch__submitted_by=user1)
    url = reverse('api:v1:import-batches-list')

    client.login(username=user2.username, password='test')
    response2 = client.get(url)
    results = json.loads(response2.content.decode('utf-8'))
    assert results['count'] == 0
    client.logout()

    client.login(username=user1.username, password='test')
    response1 = client.get(url)
    results = json.loads(response1.content.decode('utf-8'))
    assert results['count'] == 1
    assert results['results'][0]['jobs'][0]['mbid'] == job.mbid


def test_can_search_artist(factories, client):
    artist1 = factories['music.Artist']()
    artist2 = factories['music.Artist']()
    expected = [serializers.ArtistSerializerNested(artist1).data]
    url = reverse('api:v1:artists-search')
    response = client.get(url, {'query': artist1.name})
    assert json.loads(response.content.decode('utf-8')) == expected


def test_can_search_artist_by_name_start(factories, client):
    artist1 = factories['music.Artist'](name='alpha')
    artist2 = factories['music.Artist'](name='beta')
    expected = {
        'next': None,
        'previous': None,
        'count': 1,
        'results': [serializers.ArtistSerializerNested(artist1).data]
    }
    url = reverse('api:v1:artists-list')
    response = client.get(url, {'name__startswith': 'a'})

    assert expected == json.loads(response.content.decode('utf-8'))


def test_can_search_tracks(factories, client):
    track1 = factories['music.Track'](title="test track 1")
    track2 = factories['music.Track']()
    query = 'test track 1'
    expected = [serializers.TrackSerializerNested(track1).data]
    url = reverse('api:v1:tracks-search')
    response = client.get(url, {'query': query})

    assert expected == json.loads(response.content.decode('utf-8'))


@pytest.mark.parametrize('route,method', [
    ('api:v1:tags-list', 'get'),
    ('api:v1:tracks-list', 'get'),
    ('api:v1:artists-list', 'get'),
    ('api:v1:albums-list', 'get'),
])
def test_can_restrict_api_views_to_authenticated_users(db, route, method, settings, client):
    url = reverse(route)
    settings.API_AUTHENTICATION_REQUIRED = True
    response = getattr(client, method)(url)
    assert response.status_code == 401


def test_track_file_url_is_restricted_to_authenticated_users(client, factories, settings):
    settings.API_AUTHENTICATION_REQUIRED = True
    f = factories['music.TrackFile']()
    assert f.audio_file is not None
    url = f.path
    response = client.get(url)
    assert response.status_code == 401

    user = factories['users.SuperUser']()
    client.login(username=user.username, password='test')
    response = client.get(url)

    assert response.status_code == 200
    assert response['X-Accel-Redirect'] == '/_protected{}'.format(f.audio_file.url)
