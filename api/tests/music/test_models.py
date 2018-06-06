import os
import pytest

from funkwhale_api.music import models
from funkwhale_api.music import importers
from funkwhale_api.music import tasks

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def test_can_store_release_group_id_on_album(factories):
    album = factories['music.Album']()
    assert album.release_group_id is not None


def test_import_album_stores_release_group(factories):
    album_data = {
        "artist-credit": [
            {
                "artist": {
                    "disambiguation": "George Shaw",
                    "id": "62c3befb-6366-4585-b256-809472333801",
                    "name": "Adhesive Wombat",
                    "sort-name": "Wombat, Adhesive"
                }
            }
        ],
        "artist-credit-phrase": "Adhesive Wombat",
        "country": "XW",
        "date": "2013-06-05",
        "id": "a50d2a81-2a50-484d-9cb4-b9f6833f583e",
        "status": "Official",
        "title": "Marsupial Madness",
        'release-group': {'id': '447b4979-2178-405c-bfe6-46bf0b09e6c7'}
    }
    artist = factories['music.Artist'](
        mbid=album_data['artist-credit'][0]['artist']['id']
    )
    cleaned_data = models.Album.clean_musicbrainz_data(album_data)
    album = importers.load(models.Album, cleaned_data, album_data, import_hooks=[])

    assert album.release_group_id == album_data['release-group']['id']
    assert album.artist == artist


def test_import_track_from_release(factories, mocker):
    album = factories['music.Album'](
        mbid='430347cb-0879-3113-9fde-c75b658c298e')
    album_data = {
        'release': {
            'id': album.mbid,
            'title': 'Daydream Nation',
            'status': 'Official',
            'medium-count': 1,
            'medium-list': [
                {
                    'position': '1',
                    'format': 'CD',
                    'track-list': [
                        {
                            'id': '03baca8b-855a-3c05-8f3d-d3235287d84d',
                            'position': '4',
                            'number': '4',
                            'length': '417973',
                            'recording': {
                                'id': '2109e376-132b-40ad-b993-2bb6812e19d4',
                                'title': 'Teen Age Riot',
                                'length': '417973'},
                            'track_or_recording_length': '417973'
                        }
                    ],
                    'track-count': 1
                }
            ],
        }
    }
    mocked_get = mocker.patch(
        'funkwhale_api.musicbrainz.api.releases.get',
        return_value=album_data)
    track_data = album_data['release']['medium-list'][0]['track-list'][0]
    track = models.Track.get_or_create_from_release(
        '430347cb-0879-3113-9fde-c75b658c298e',
        track_data['recording']['id'],
    )[0]
    mocked_get.assert_called_once_with(
        album.mbid, includes=models.Album.api_includes)
    assert track.title == track_data['recording']['title']
    assert track.mbid == track_data['recording']['id']
    assert track.album == album
    assert track.artist == album.artist
    assert track.position == int(track_data['position'])

def test_import_job_is_bound_to_track_file(factories, mocker):
    track = factories['music.Track']()
    job = factories['music.ImportJob'](mbid=track.mbid)

    mocker.patch('funkwhale_api.music.models.TrackFile.download_file')
    tasks.import_job_run(import_job_id=job.pk)
    job.refresh_from_db()
    assert job.track_file.track == track


@pytest.mark.parametrize('status', ['pending', 'errored', 'finished'])
def test_saving_job_updates_batch_status(status,factories, mocker):
    batch = factories['music.ImportBatch']()

    assert batch.status == 'pending'

    job = factories['music.ImportJob'](batch=batch, status=status)

    batch.refresh_from_db()

    assert batch.status == status


@pytest.mark.parametrize('extention,mimetype', [
    ('ogg', 'audio/ogg'),
    ('mp3', 'audio/mpeg'),
])
def test_audio_track_mime_type(extention, mimetype, factories):

    name = '.'.join(['test', extention])
    path = os.path.join(DATA_DIR, name)
    tf = factories['music.TrackFile'](audio_file__from_path=path)

    assert tf.mimetype == mimetype


def test_track_file_file_name(factories):
    name = 'test.mp3'
    path = os.path.join(DATA_DIR, name)
    tf = factories['music.TrackFile'](audio_file__from_path=path)

    assert tf.filename == tf.track.full_name + '.mp3'


def test_track_get_file_size(factories):
    name = 'test.mp3'
    path = os.path.join(DATA_DIR, name)
    tf = factories['music.TrackFile'](audio_file__from_path=path)

    assert tf.get_file_size() == 297745


def test_track_get_file_size_federation(factories):
    tf = factories['music.TrackFile'](
        federation=True,
        library_track__with_audio_file=True)

    assert tf.get_file_size() == tf.library_track.audio_file.size


def test_track_get_file_size_in_place(factories):
    name = 'test.mp3'
    path = os.path.join(DATA_DIR, name)
    tf = factories['music.TrackFile'](
        in_place=True, source='file://{}'.format(path))

    assert tf.get_file_size() == 297745


def test_album_get_image_content(factories):
    album = factories['music.Album']()
    album.get_image(data={'content': b'test', 'mimetype':'image/jpeg'})
    album.refresh_from_db()

    assert album.cover.read() == b'test'
