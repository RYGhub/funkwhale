import datetime
import os
import pytest
import uuid

from funkwhale_api.music import metadata

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.parametrize('field,value', [
    ('title', 'Peer Gynt Suite no. 1, op. 46: I. Morning'),
    ('artist', 'Edvard Grieg'),
    ('album', 'Peer Gynt Suite no. 1, op. 46'),
    ('date', datetime.date(2012, 8, 15)),
    ('track_number', 1),
    ('musicbrainz_albumid', uuid.UUID('a766da8b-8336-47aa-a3ee-371cc41ccc75')),
    ('musicbrainz_recordingid', uuid.UUID('bd21ac48-46d8-4e78-925f-d9cc2a294656')),
    ('musicbrainz_artistid', uuid.UUID('013c8e5b-d72a-4cd3-8dee-6c64d6125823')),
])
def test_can_get_metadata_from_ogg_file(field, value):
    path = os.path.join(DATA_DIR, 'test.ogg')
    data = metadata.Metadata(path)

    assert data.get(field) == value


@pytest.mark.parametrize('field,value', [
    ('title', 'Bend'),
    ('artist', 'Binärpilot'),
    ('album', 'You Can\'t Stop Da Funk'),
    ('date', datetime.date(2006, 2, 7)),
    ('track_number', 1),
    ('musicbrainz_albumid', uuid.UUID('ce40cdb1-a562-4fd8-a269-9269f98d4124')),
    ('musicbrainz_recordingid', uuid.UUID('f269d497-1cc0-4ae4-a0c4-157ec7d73fcb')),
    ('musicbrainz_artistid', uuid.UUID('9c6bddde-6228-4d9f-ad0d-03f6fcb19e13')),
])
def test_can_get_metadata_from_id3_mp3_file(field, value):
    path = os.path.join(DATA_DIR, 'test.mp3')
    data = metadata.Metadata(path)

    assert data.get(field) == value
