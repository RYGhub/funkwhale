import unittest
import os
import datetime
from test_plus.test import TestCase
from funkwhale_api.music import metadata

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


class TestMetadata(TestCase):

    def test_can_get_metadata_from_ogg_file(self, *mocks):
        path = os.path.join(DATA_DIR, 'test.ogg')
        data = metadata.Metadata(path)

        self.assertEqual(
            data.get('title'),
            'Peer Gynt Suite no. 1, op. 46: I. Morning'
        )
        self.assertEqual(
            data.get('artist'),
            'Edvard Grieg'
        )
        self.assertEqual(
            data.get('album'),
            'Peer Gynt Suite no. 1, op. 46'
        )
        self.assertEqual(
            data.get('date'),
            datetime.date(2012, 8, 15),
        )
        self.assertEqual(
            data.get('track_number'),
            1
        )

        self.assertEqual(
            data.get('musicbrainz_albumid'),
            'a766da8b-8336-47aa-a3ee-371cc41ccc75')
        self.assertEqual(
            data.get('musicbrainz_recordingid'),
            'bd21ac48-46d8-4e78-925f-d9cc2a294656')
        self.assertEqual(
            data.get('musicbrainz_artistid'),
            '013c8e5b-d72a-4cd3-8dee-6c64d6125823')

    def test_can_get_metadata_from_id3_mp3_file(self, *mocks):
        path = os.path.join(DATA_DIR, 'test.mp3')
        data = metadata.Metadata(path)

        self.assertEqual(
            data.get('title'),
            'Bend'
        )
        self.assertEqual(
            data.get('artist'),
            'Binärpilot'
        )
        self.assertEqual(
            data.get('album'),
            'You Can\'t Stop Da Funk'
        )
        self.assertEqual(
            data.get('date'),
            datetime.date(2006, 2, 7),
        )
        self.assertEqual(
            data.get('track_number'),
            1
        )

        self.assertEqual(
            data.get('musicbrainz_albumid'),
            'ce40cdb1-a562-4fd8-a269-9269f98d4124')
        self.assertEqual(
            data.get('musicbrainz_recordingid'),
            'f269d497-1cc0-4ae4-a0c4-157ec7d73fcb')
        self.assertEqual(
            data.get('musicbrainz_artistid'),
            '9c6bddde-6228-4d9f-ad0d-03f6fcb19e13')
