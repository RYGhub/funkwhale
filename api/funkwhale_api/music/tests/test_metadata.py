import unittest
import os
from test_plus.test import TestCase
from funkwhale_api.music import metadata

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


class TestMetadata(TestCase):

    def test_can_get_metadata_from_file(self, *mocks):
        path = os.path.join(DATA_DIR, 'test.ogg')
        data = metadata.Metadata(path)

        self.assertEqual(
            data.get('musicbrainz_albumid'),
            'a766da8b-8336-47aa-a3ee-371cc41ccc75')
        self.assertEqual(
            data.get('musicbrainz_trackid'),
            'bd21ac48-46d8-4e78-925f-d9cc2a294656')
        self.assertEqual(
            data.get('musicbrainz_artistid'),
            '013c8e5b-d72a-4cd3-8dee-6c64d6125823')

        self.assertEqual(data.release, data.get('musicbrainz_albumid'))
        self.assertEqual(data.artist, data.get('musicbrainz_artistid'))
        self.assertEqual(data.recording, data.get('musicbrainz_trackid'))
