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
    ('title', 'Drei Kreuze (dass wir hier sind)'),
    ('artist', 'Die Toten Hosen'),
    ('album', 'Ballast der Republik'),
    ('date', datetime.date(2012, 5, 4)),
    ('track_number', 1),
    ('musicbrainz_albumid', uuid.UUID('1f0441ad-e609-446d-b355-809c445773cf')),
    ('musicbrainz_recordingid', uuid.UUID('124d0150-8627-46bc-bc14-789a3bc960c8')),
    ('musicbrainz_artistid', uuid.UUID('c3bc80a6-1f4a-4e17-8cf0-6b1efe8302f1')),
])
def test_can_get_metadata_from_ogg_theora_file(field, value):
    path = os.path.join(DATA_DIR, 'test_theora.ogg')
    data = metadata.Metadata(path)

    assert data.get(field) == value


@pytest.mark.parametrize('field,value', [
    ('title', 'Bend'),
    ('artist', 'Bindrpilot'),
    ('album', 'You Can\'t Stop Da Funk'),
    ('date', datetime.date(2006, 2, 7)),
    ('track_number', 2),
    ('musicbrainz_albumid', uuid.UUID('ce40cdb1-a562-4fd8-a269-9269f98d4124')),
    ('musicbrainz_recordingid', uuid.UUID('f269d497-1cc0-4ae4-a0c4-157ec7d73fcb')),
    ('musicbrainz_artistid', uuid.UUID('9c6bddde-6228-4d9f-ad0d-03f6fcb19e13')),
])
def test_can_get_metadata_from_id3_mp3_file(field, value):
    path = os.path.join(DATA_DIR, 'test.mp3')
    data = metadata.Metadata(path)

    assert data.get(field) == value


@pytest.mark.parametrize('name', ['test.mp3', 'sample.flac'])
def test_can_get_pictures(name):
    path = os.path.join(DATA_DIR, name)
    data = metadata.Metadata(path)

    pictures = data.get('pictures')
    assert len(pictures) == 1
    cover_data = data.get_picture('cover_front')
    assert cover_data['mimetype'].startswith('image/')
    assert len(cover_data['content']) > 0
    assert type(cover_data['content']) == bytes
    assert type(cover_data['description']) == str


@pytest.mark.parametrize('field,value', [
    ('title', '999,999'),
    ('artist', 'Nine Inch Nails'),
    ('album', 'The Slip'),
    ('date', datetime.date(2008, 5, 5)),
    ('track_number', 1),
    ('musicbrainz_albumid', uuid.UUID('12b57d46-a192-499e-a91f-7da66790a1c1')),
    ('musicbrainz_recordingid', uuid.UUID('30f3f33e-8d0c-4e69-8539-cbd701d18f28')),
    ('musicbrainz_artistid', uuid.UUID('b7ffd2af-418f-4be2-bdd1-22f8b48613da')),
])
def test_can_get_metadata_from_flac_file(field, value):
    path = os.path.join(DATA_DIR, 'sample.flac')
    data = metadata.Metadata(path)

    assert data.get(field) == value


def test_can_get_metadata_from_flac_file_not_crash_if_empty():
    path = os.path.join(DATA_DIR, 'sample.flac')
    data = metadata.Metadata(path)

    with pytest.raises(metadata.TagNotFound):
        data.get('test')


@pytest.mark.parametrize('field_name', [
    'musicbrainz_artistid',
    'musicbrainz_albumid',
    'musicbrainz_recordingid',
])
def test_mbid_clean_keeps_only_first(field_name):
    u1 = str(uuid.uuid4())
    u2 = str(uuid.uuid4())
    field = metadata.VALIDATION[field_name]
    result = field.to_python('/'.join([u1, u2]))

    assert str(result) == u1
