import json
import unittest
from test_plus.test import TestCase
from django.urls import reverse

from funkwhale_api.music import models
from funkwhale_api.musicbrainz import api
from funkwhale_api.music import serializers
from funkwhale_api.users.models import User
from funkwhale_api.music import lyrics as lyrics_utils

from .mocking import lyricswiki
from . import factories
from . import data as api_data



class TestLyrics(TestCase):

    @unittest.mock.patch('funkwhale_api.music.lyrics._get_html',
                         return_value=lyricswiki.content)
    def test_works_import_lyrics_if_any(self, *mocks):
        lyrics = factories.LyricsFactory(
            url='http://lyrics.wikia.com/System_Of_A_Down:Chop_Suey!')

        lyrics.fetch_content()
        self.assertIn(
            'Grab a brush and put on a little makeup',
            lyrics.content,
        )

    def test_clean_content(self):
        c = """<div class="lyricbox">Hello<br /><script>alert('hello');</script>Is it me you're looking for?<br /></div>"""
        d = lyrics_utils.extract_content(c)
        d = lyrics_utils.clean_content(d)

        expected = """Hello
Is it me you're looking for?
"""
        self.assertEqual(d, expected)

    def test_markdown_rendering(self):
        content = """Hello
Is it me you're looking for?"""

        l = factories.LyricsFactory(content=content)

        expected = "<p>Hello<br />Is it me you're looking for?</p>"
        self.assertHTMLEqual(expected, l.content_rendered)

    @unittest.mock.patch('funkwhale_api.musicbrainz.api.works.get',
                         return_value=api_data.works['get']['chop_suey'])
    @unittest.mock.patch('funkwhale_api.musicbrainz.api.recordings.get',
                         return_value=api_data.tracks['get']['chop_suey'])
    @unittest.mock.patch('funkwhale_api.music.lyrics._get_html',
                         return_value=lyricswiki.content)
    def test_works_import_lyrics_if_any(self, *mocks):
        track = factories.TrackFactory(
            work=None,
            mbid='07ca77cf-f513-4e9c-b190-d7e24bbad448')

        url = reverse('api:v1:tracks-lyrics', kwargs={'pk': track.pk})
        user = User.objects.create_user(
            username='test', email='test@test.com', password='test')
        self.client.login(username=user.username, password='test')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        track.refresh_from_db()
        lyrics = models.Lyrics.objects.latest('id')
        work = models.Work.objects.latest('id')

        self.assertEqual(track.work, work)
        self.assertEqual(lyrics.work, work)
