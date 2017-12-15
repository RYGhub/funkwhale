import json
import unittest
from test_plus.test import TestCase
from django.core.urlresolvers import reverse

from funkwhale_api.music import models
from funkwhale_api.musicbrainz import api
from funkwhale_api.music import serializers
from funkwhale_api.music.tests import factories
from funkwhale_api.users.models import User

from . import data as api_data


class TestWorks(TestCase):

    @unittest.mock.patch('funkwhale_api.musicbrainz.api.works.get',
                         return_value=api_data.works['get']['chop_suey'])
    def test_can_import_work(self, *mocks):
        recording = factories.TrackFactory(
            mbid='07ca77cf-f513-4e9c-b190-d7e24bbad448')
        mbid = 'e2ecabc4-1b9d-30b2-8f30-3596ec423dc5'
        work = models.Work.create_from_api(id=mbid)

        self.assertEqual(work.title, 'Chop Suey!')
        self.assertEqual(work.nature, 'song')
        self.assertEqual(work.language, 'eng')
        self.assertEqual(work.mbid, mbid)

        # a imported work should also be linked to corresponding recordings

        recording.refresh_from_db()
        self.assertEqual(recording.work, work)

    @unittest.mock.patch('funkwhale_api.musicbrainz.api.works.get',
                         return_value=api_data.works['get']['chop_suey'])
    @unittest.mock.patch('funkwhale_api.musicbrainz.api.recordings.get',
                         return_value=api_data.tracks['get']['chop_suey'])
    def test_can_get_work_from_recording(self, *mocks):
        recording = factories.TrackFactory(
            work=None,
            mbid='07ca77cf-f513-4e9c-b190-d7e24bbad448')
        mbid = 'e2ecabc4-1b9d-30b2-8f30-3596ec423dc5'

        self.assertEqual(recording.work, None)

        work = recording.get_work()

        self.assertEqual(work.title, 'Chop Suey!')
        self.assertEqual(work.nature, 'song')
        self.assertEqual(work.language, 'eng')
        self.assertEqual(work.mbid, mbid)

        recording.refresh_from_db()
        self.assertEqual(recording.work, work)

    @unittest.mock.patch('funkwhale_api.musicbrainz.api.works.get',
                         return_value=api_data.works['get']['chop_suey'])
    def test_works_import_lyrics_if_any(self, *mocks):
        mbid = 'e2ecabc4-1b9d-30b2-8f30-3596ec423dc5'
        work = models.Work.create_from_api(id=mbid)

        lyrics = models.Lyrics.objects.latest('id')
        self.assertEqual(lyrics.work, work)
        self.assertEqual(
            lyrics.url, 'http://lyrics.wikia.com/System_Of_A_Down:Chop_Suey!')
