import os
import datetime
import unittest
from test_plus.test import TestCase

from funkwhale_api.providers.audiofile import tasks

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


class TestAudioFile(TestCase):
    def test_can_import_single_audio_file(self, *mocks):
        metadata = {
            'artist': ['Test artist'],
            'album': ['Test album'],
            'title': ['Test track'],
            'TRACKNUMBER': ['4'],
            'date': ['2012-08-15'],
            'musicbrainz_albumid': ['a766da8b-8336-47aa-a3ee-371cc41ccc75'],
            'musicbrainz_trackid': ['bd21ac48-46d8-4e78-925f-d9cc2a294656'],
            'musicbrainz_artistid': ['013c8e5b-d72a-4cd3-8dee-6c64d6125823'],
        }

        m1 = unittest.mock.patch('mutagen.File', return_value=metadata)
        m2 = unittest.mock.patch(
            'funkwhale_api.music.metadata.Metadata.get_file_type',
            return_value='OggVorbis',
        )
        with m1, m2:
            track_file = tasks.from_path(
                os.path.join(DATA_DIR, 'dummy_file.ogg'))

        self.assertEqual(
            track_file.track.title, metadata['title'][0])
        self.assertEqual(
            track_file.track.mbid, metadata['musicbrainz_trackid'][0])
        self.assertEqual(
            track_file.track.position, 4)
        self.assertEqual(
            track_file.track.album.title, metadata['album'][0])
        self.assertEqual(
            track_file.track.album.mbid,
            metadata['musicbrainz_albumid'][0])
        self.assertEqual(
            track_file.track.album.release_date, datetime.date(2012, 8, 15))
        self.assertEqual(
            track_file.track.artist.name, metadata['artist'][0])
        self.assertEqual(
            track_file.track.artist.mbid,
            metadata['musicbrainz_artistid'][0])
