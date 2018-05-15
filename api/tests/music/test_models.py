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
