import json
import pytest

from django.urls import reverse

from funkwhale_api.music import tasks


def test_create_import_can_bind_to_request(
        artists, albums, mocker, factories, superuser_api_client):
    request = factories['requests.ImportRequest']()

    mocker.patch('funkwhale_api.music.tasks.import_job_run')
    mocker.patch(
        'funkwhale_api.musicbrainz.api.artists.get',
        return_value=artists['get']['soad'])
    mocker.patch(
        'funkwhale_api.musicbrainz.api.images.get_front',
        return_value=b'')
    mocker.patch(
        'funkwhale_api.musicbrainz.api.releases.get',
        return_value=albums['get_with_includes']['hypnotize'])
    payload = {
        'releaseId': '47ae093f-1607-49a3-be11-a15d335ccc94',
        'importRequest': request.pk,
        'tracks': [
            {
                'mbid': '1968a9d6-8d92-4051-8f76-674e157b6eed',
                'source': 'https://www.youtube.com/watch?v=1111111111',
            }
        ]
    }
    url = reverse('api:v1:submit-album')
    response = superuser_api_client.post(
        url, json.dumps(payload), content_type='application/json')
    batch = request.import_batches.latest('id')

    assert batch.import_request == request


def test_import_job_from_federation_no_musicbrainz(factories):
    lt = factories['federation.LibraryTrack'](
        artist_name='Hello',
        album_title='World',
        title='Ping',
    )
    job = factories['music.ImportJob'](
        federation=True,
        library_track=lt,
    )

    tasks.import_job_run(import_job_id=job.pk)
    job.refresh_from_db()

    tf = job.track_file
    assert tf.mimetype == lt.audio_mimetype
    assert tf.library_track == job.library_track
    assert tf.track.title == 'Ping'
    assert tf.track.artist.name == 'Hello'
    assert tf.track.album.title == 'World'


def test_import_job_from_federation_musicbrainz_recording(factories, mocker):
    t = factories['music.Track']()
    track_from_api = mocker.patch(
        'funkwhale_api.music.models.Track.get_or_create_from_api',
        return_value=t)
    lt = factories['federation.LibraryTrack'](
        metadata__recording__musicbrainz=True,
        artist_name='Hello',
        album_title='World',
    )
    job = factories['music.ImportJob'](
        federation=True,
        library_track=lt,
    )

    tasks.import_job_run(import_job_id=job.pk)
    job.refresh_from_db()

    tf = job.track_file
    assert tf.mimetype == lt.audio_mimetype
    assert tf.library_track == job.library_track
    assert tf.track == t
    track_from_api.assert_called_once_with(
        mbid=lt.metadata['recording']['musicbrainz_id'])


def test_import_job_from_federation_musicbrainz_release(factories, mocker):
    a = factories['music.Album']()
    album_from_api = mocker.patch(
        'funkwhale_api.music.models.Album.get_or_create_from_api',
        return_value=a)
    lt = factories['federation.LibraryTrack'](
        metadata__release__musicbrainz=True,
        artist_name='Hello',
        title='Ping',
    )
    job = factories['music.ImportJob'](
        federation=True,
        library_track=lt,
    )

    tasks.import_job_run(import_job_id=job.pk)
    job.refresh_from_db()

    tf = job.track_file
    assert tf.mimetype == lt.audio_mimetype
    assert tf.library_track == job.library_track
    assert tf.track.title == 'Ping'
    assert tf.track.artist == a.artist
    assert tf.track.album == a

    album_from_api.assert_called_once_with(
        mbid=lt.metadata['release']['musicbrainz_id'])


def test_import_job_from_federation_musicbrainz_artist(factories, mocker):
    a = factories['music.Artist']()
    artist_from_api = mocker.patch(
        'funkwhale_api.music.models.Artist.get_or_create_from_api',
        return_value=a)
    lt = factories['federation.LibraryTrack'](
        metadata__artist__musicbrainz=True,
        album_title='World',
        title='Ping',
    )
    job = factories['music.ImportJob'](
        federation=True,
        library_track=lt,
    )

    tasks.import_job_run(import_job_id=job.pk)
    job.refresh_from_db()

    tf = job.track_file
    assert tf.mimetype == lt.audio_mimetype
    assert tf.library_track == job.library_track

    assert tf.track.title == 'Ping'
    assert tf.track.artist == a
    assert tf.track.album.artist == a
    assert tf.track.album.title == 'World'

    artist_from_api.assert_called_once_with(
        mbid=lt.metadata['artist']['musicbrainz_id'])
