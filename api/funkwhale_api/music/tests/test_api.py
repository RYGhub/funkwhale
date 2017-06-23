import json
import unittest
from test_plus.test import TestCase
from django.core.urlresolvers import reverse

from funkwhale_api.music import models
from funkwhale_api.utils.tests import TMPDirTestCaseMixin
from funkwhale_api.musicbrainz import api
from funkwhale_api.music import serializers
from funkwhale_api.users.models import User

from . import data as api_data

class TestAPI(TMPDirTestCaseMixin, TestCase):

    @unittest.mock.patch('funkwhale_api.musicbrainz.api.artists.get', return_value=api_data.artists['get']['adhesive_wombat'])
    @unittest.mock.patch('funkwhale_api.musicbrainz.api.releases.get', return_value=api_data.albums['get']['marsupial'])
    @unittest.mock.patch('funkwhale_api.musicbrainz.api.recordings.get', return_value=api_data.tracks['get']['8bitadventures'])
    @unittest.mock.patch('funkwhale_api.music.models.TrackFile.download_file', return_value=None)
    def test_can_submit_youtube_url_for_track_import(self, *mocks):
        mbid = '9968a9d6-8d92-4051-8f76-674e157b6eed'
        video_id = 'tPEE9ZwTmy0'
        url = reverse('api:submit-single')
        user = User.objects.create_superuser(username='test', email='test@test.com', password='test')
        self.client.login(username=user.username, password='test')
        response = self.client.post(url, {'import_url': 'https://www.youtube.com/watch?v={0}'.format(video_id), 'mbid': mbid})
        track = models.Track.objects.get(mbid=mbid)
        self.assertEqual(track.artist.name, 'Adhesive Wombat')
        self.assertEqual(track.album.title, 'Marsupial Madness')
        # self.assertIn(video_id, track.files.first().audio_file.name)

    def test_import_creates_an_import_with_correct_data(self):
        user = User.objects.create_superuser(username='test', email='test@test.com', password='test')
        mbid = '9968a9d6-8d92-4051-8f76-674e157b6eed'
        video_id = 'tPEE9ZwTmy0'
        url = reverse('api:submit-single')
        self.client.login(username=user.username, password='test')
        with self.settings(CELERY_ALWAYS_EAGER=False):
            response = self.client.post(url, {'import_url': 'https://www.youtube.com/watch?v={0}'.format(video_id), 'mbid': mbid})

        batch = models.ImportBatch.objects.latest('id')
        self.assertEqual(batch.jobs.count(), 1)
        self.assertEqual(batch.submitted_by, user)
        self.assertEqual(batch.status, 'pending')
        job = batch.jobs.first()
        self.assertEqual(str(job.mbid), mbid)
        self.assertEqual(job.status, 'pending')
        self.assertEqual(job.source, 'https://www.youtube.com/watch?v={0}'.format(video_id))

    @unittest.mock.patch('funkwhale_api.musicbrainz.api.artists.get', return_value=api_data.artists['get']['soad'])
    @unittest.mock.patch('funkwhale_api.musicbrainz.api.images.get_front', return_value=b'')
    @unittest.mock.patch('funkwhale_api.musicbrainz.api.releases.get', return_value=api_data.albums['get_with_includes']['hypnotize'])
    def test_can_import_whole_album(self, *mocks):
        user = User.objects.create_superuser(username='test', email='test@test.com', password='test')
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
        url = reverse('api:submit-album')
        self.client.login(username=user.username, password='test')
        with self.settings(CELERY_ALWAYS_EAGER=False):
            response = self.client.post(url, json.dumps(payload), content_type="application/json")

        batch = models.ImportBatch.objects.latest('id')
        self.assertEqual(batch.jobs.count(), 3)
        self.assertEqual(batch.submitted_by, user)
        self.assertEqual(batch.status, 'pending')

        album = models.Album.objects.latest('id')
        self.assertEqual(str(album.mbid), '47ae093f-1607-49a3-be11-a15d335ccc94')
        medium_data = api_data.albums['get_with_includes']['hypnotize']['release']['medium-list'][0]
        self.assertEqual(int(medium_data['track-count']), album.tracks.all().count())

        for track in medium_data['track-list']:
            instance = models.Track.objects.get(mbid=track['recording']['id'])
            self.assertEqual(instance.title, track['recording']['title'])
            self.assertEqual(instance.position, int(track['position']))
            self.assertEqual(instance.title, track['recording']['title'])

        for row in payload['tracks']:
            job = models.ImportJob.objects.get(mbid=row['mbid'])
            self.assertEqual(str(job.mbid), row['mbid'])
            self.assertEqual(job.status, 'pending')
            self.assertEqual(job.source, row['source'])

    @unittest.mock.patch('funkwhale_api.musicbrainz.api.artists.get', return_value=api_data.artists['get']['soad'])
    @unittest.mock.patch('funkwhale_api.musicbrainz.api.images.get_front', return_value=b'')
    @unittest.mock.patch('funkwhale_api.musicbrainz.api.releases.get', return_value=api_data.albums['get_with_includes']['hypnotize'])
    def test_can_import_whole_artist(self, *mocks):
        user = User.objects.create_superuser(username='test', email='test@test.com', password='test')
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
        url = reverse('api:submit-artist')
        self.client.login(username=user.username, password='test')
        with self.settings(CELERY_ALWAYS_EAGER=False):
            response = self.client.post(url, json.dumps(payload), content_type="application/json")

        batch = models.ImportBatch.objects.latest('id')
        self.assertEqual(batch.jobs.count(), 3)
        self.assertEqual(batch.submitted_by, user)
        self.assertEqual(batch.status, 'pending')

        album = models.Album.objects.latest('id')
        self.assertEqual(str(album.mbid), '47ae093f-1607-49a3-be11-a15d335ccc94')
        medium_data = api_data.albums['get_with_includes']['hypnotize']['release']['medium-list'][0]
        self.assertEqual(int(medium_data['track-count']), album.tracks.all().count())

        for track in medium_data['track-list']:
            instance = models.Track.objects.get(mbid=track['recording']['id'])
            self.assertEqual(instance.title, track['recording']['title'])
            self.assertEqual(instance.position, int(track['position']))
            self.assertEqual(instance.title, track['recording']['title'])

        for row in payload['albums'][0]['tracks']:
            job = models.ImportJob.objects.get(mbid=row['mbid'])
            self.assertEqual(str(job.mbid), row['mbid'])
            self.assertEqual(job.status, 'pending')
            self.assertEqual(job.source, row['source'])

    def test_user_can_query_api_for_his_own_batches(self):
        user1 = User.objects.create_superuser(username='test1', email='test1@test.com', password='test')
        user2 = User.objects.create_superuser(username='test2', email='test2@test.com', password='test')
        mbid = '9968a9d6-8d92-4051-8f76-674e157b6eed'
        source = 'https://www.youtube.com/watch?v=tPEE9ZwTmy0'

        batch = models.ImportBatch.objects.create(submitted_by=user1)
        job = models.ImportJob.objects.create(batch=batch, mbid=mbid, source=source)

        url = reverse('api:import-batches-list')

        self.client.login(username=user2.username, password='test')
        response2 = self.client.get(url)
        self.assertJSONEqual(response2.content.decode('utf-8'), '{"count":0,"next":null,"previous":null,"results":[]}')
        self.client.logout()

        self.client.login(username=user1.username, password='test')
        response1 = self.client.get(url)
        self.assertIn(mbid, response1.content.decode('utf-8'))

    def test_can_search_artist(self):
        artist1 = models.Artist.objects.create(name='Test1')
        artist2 = models.Artist.objects.create(name='Test2')
        query = 'test1'
        expected = '[{0}]'.format(json.dumps(serializers.ArtistSerializerNested(artist1).data))
        url = self.reverse('api:artists-search')
        response = self.client.get(url + '?query={0}'.format(query))

        self.assertJSONEqual(expected, json.loads(response.content.decode('utf-8')))

    def test_can_search_tracks(self):
        artist1 = models.Artist.objects.create(name='Test1')
        artist2 = models.Artist.objects.create(name='Test2')
        track1 = models.Track.objects.create(artist=artist1, title="test_track1")
        track2 = models.Track.objects.create(artist=artist2, title="test_track2")
        query = 'test track 1'
        expected = '[{0}]'.format(json.dumps(serializers.TrackSerializerNested(track1).data))
        url = self.reverse('api:tracks-search')
        response = self.client.get(url + '?query={0}'.format(query))

        self.assertJSONEqual(expected, json.loads(response.content.decode('utf-8')))

    def test_can_restrict_api_views_to_authenticated_users(self):
        urls = [
            ('api:tags-list', 'get'),
            ('api:tracks-list', 'get'),
            ('api:artists-list', 'get'),
            ('api:albums-list', 'get'),
        ]

        for route_name, method in urls:
            url = self.reverse(route_name)
            with self.settings(API_AUTHENTICATION_REQUIRED=True):
                response = getattr(self.client, method)(url)
            self.assertEqual(response.status_code, 401)

        user = User.objects.create_superuser(username='test', email='test@test.com', password='test')
        self.client.login(username=user.username, password='test')

        for route_name, method in urls:
            url = self.reverse(route_name)
            with self.settings(API_AUTHENTICATION_REQUIRED=False):
                response = getattr(self.client, method)(url)
            self.assertEqual(response.status_code, 200)
