import acoustid
import datetime
import os

from .music import data as api_data
from funkwhale_api.providers.audiofile import tasks

DATA_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'files'
)


def test_import_file_with_acoustid(db, mocker, preferences):
    mbid = api_data.tracks['get']['8bitadventures']['recording']['id']
    payload = {
        'results': [{
            'id': 'e475bf79-c1ce-4441-bed7-1e33f226c0a2',
            'recordings': [{'id': mbid}],
            'score': 0.86
        }]
    }
    path = os.path.join(DATA_DIR, 'dummy_file.ogg')
    m = mocker.patch('acoustid.match', return_value=payload)
    mocker.patch(
        'funkwhale_api.musicbrainz.api.artists.get',
        return_value=api_data.artists['get']['adhesive_wombat'])
    mocker.patch(
        'funkwhale_api.musicbrainz.api.releases.get',
        return_value=api_data.albums['get']['marsupial'])
    mocker.patch(
        'funkwhale_api.musicbrainz.api.recordings.get',
        return_value=api_data.tracks['get']['8bitadventures'])
    track_file = tasks.from_path(path)
    result = payload['results'][0]

    assert track_file.acoustid_track_id == result['id']
    assert track_file.track.mbid == result['recordings'][0]['id']
    m.assert_called_once_with('', path, parse=False)


def test_can_import_single_audio_file_without_acoustid(db, mocker):
    mocker.patch('acoustid.match', side_effect=acoustid.WebServiceError('test'))
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
    m1 = mocker.patch('mutagen.File', return_value=metadata)
    m2 = mocker.patch(
        'funkwhale_api.music.metadata.Metadata.get_file_type',
        return_value='OggVorbis',
    )
    track_file = tasks.from_path(os.path.join(DATA_DIR, 'dummy_file.ogg'))
    track = track_file.track

    assert track.title == metadata['title'][0]
    assert track.mbid == metadata['musicbrainz_trackid'][0]
    assert track.position == 4
    assert track.album.title == metadata['album'][0]
    assert track.album.mbid == metadata['musicbrainz_albumid'][0]
    assert track.album.release_date == datetime.date(2012, 8, 15)
    assert track.artist.name == metadata['artist'][0]
    assert track.artist.mbid == metadata['musicbrainz_artistid'][0]
