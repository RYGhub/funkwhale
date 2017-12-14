import pytest

from funkwhale_api.music import models
from funkwhale_api.music import importers
from . import factories


def test_can_store_release_group_id_on_album(db):
    album = factories.AlbumFactory()
    assert album.release_group_id is not None


def test_import_album_stores_release_group(db):

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
    artist = factories.ArtistFactory(
        mbid=album_data['artist-credit'][0]['artist']['id']
    )
    cleaned_data = models.Album.clean_musicbrainz_data(album_data)
    album = importers.load(models.Album, cleaned_data, album_data, import_hooks=[])

    assert album.release_group_id == album_data['release-group']['id']
    assert album.artist == artist


def test_import_job_is_bound_to_track_file(db, mocker):
    track = factories.TrackFactory()
    job = factories.ImportJobFactory(mbid=track.mbid)

    mocker.patch('funkwhale_api.music.models.TrackFile.download_file')
    job.run()
    job.refresh_from_db()
    assert job.track_file.track == track
