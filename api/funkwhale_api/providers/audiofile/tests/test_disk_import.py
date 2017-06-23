import os
import datetime
import unittest
from test_plus.test import TestCase

from funkwhale_api.providers.audiofile import importer

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


class TestAudioFile(TestCase):
    def test_can_import_single_audio_file(self, *mocks):
        metadata = {
            'artist': ['Test artist'],
            'album': ['Test album'],
            'title': ['Test track'],
            'tracknumber': ['4'],
            'date': ['2012-08-15']
        }

        with unittest.mock.patch('mutagen.File', return_value=metadata):
            track_file = importer.from_path(
                os.path.join(DATA_DIR, 'dummy_file.ogg'))

        self.assertEqual(
            track_file.track.title, metadata['title'][0])
        self.assertEqual(
            track_file.track.position, 4)
        self.assertEqual(
            track_file.track.album.title, metadata['album'][0])
        self.assertEqual(
            track_file.track.album.release_date, datetime.date(2012, 8, 15))
        self.assertEqual(
            track_file.track.artist.name, metadata['artist'][0])
