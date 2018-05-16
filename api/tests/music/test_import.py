import json
import os
import pytest

from django.urls import reverse

from funkwhale_api.federation import actors
from funkwhale_api.federation import serializers as federation_serializers
from funkwhale_api.music import tasks

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


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


def test_import_job_from_federation_no_musicbrainz(factories, mocker):
    mocker.patch(
        'funkwhale_api.music.utils.get_audio_file_data',
        return_value={'bitrate': 24, 'length': 666})
    mocker.patch(
        'funkwhale_api.music.models.TrackFile.get_file_size',
        return_value=42)
    lt = factories['federation.LibraryTrack'](
        artist_name='Hello',
        album_title='World',
        title='Ping',
        metadata__length=42,
        metadata__bitrate=43,
        metadata__size=44,
    )
    job = factories['music.ImportJob'](
        federation=True,
        library_track=lt,
    )

    tasks.import_job_run(import_job_id=job.pk)
    job.refresh_from_db()

    tf = job.track_file
    assert tf.mimetype == lt.audio_mimetype
    assert tf.duration == 42
    assert tf.bitrate == 43
    assert tf.size == 44
    assert tf.library_track == job.library_track
    assert tf.track.title == 'Ping'
    assert tf.track.artist.name == 'Hello'
    assert tf.track.album.title == 'World'


def test_import_job_from_federation_musicbrainz_recording(factories, mocker):
    t = factories['music.Track']()
    track_from_api = mocker.patch(
        'funkwhale_api.music.models.Track.get_or_create_from_api',
        return_value=(t, True))
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
        return_value=(a, True))
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
        return_value=(a, True))
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


def test_import_job_run_triggers_notifies_followers(
        factories, mocker, tmpfile):
    mocker.patch(
        'funkwhale_api.downloader.download',
        return_value={'audio_file_path': tmpfile.name})
    mocked_notify = mocker.patch(
        'funkwhale_api.music.tasks.import_batch_notify_followers.delay')
    batch = factories['music.ImportBatch']()
    job = factories['music.ImportJob'](
        finished=True, batch=batch)
    track = factories['music.Track'](mbid=job.mbid)

    batch.update_status()
    batch.refresh_from_db()

    assert batch.status == 'finished'

    mocked_notify.assert_called_once_with(import_batch_id=batch.pk)


def test_import_batch_notifies_followers_skip_on_disabled_federation(
        preferences, factories, mocker):
    mocked_deliver = mocker.patch('funkwhale_api.federation.activity.deliver')
    batch = factories['music.ImportBatch'](finished=True)
    preferences['federation__enabled'] = False
    tasks.import_batch_notify_followers(import_batch_id=batch.pk)

    mocked_deliver.assert_not_called()


def test_import_batch_notifies_followers_skip_on_federation_import(
        factories, mocker):
    mocked_deliver = mocker.patch('funkwhale_api.federation.activity.deliver')
    batch = factories['music.ImportBatch'](finished=True, federation=True)
    tasks.import_batch_notify_followers(import_batch_id=batch.pk)

    mocked_deliver.assert_not_called()


def test_import_batch_notifies_followers(
        factories, mocker):
    library_actor = actors.SYSTEM_ACTORS['library'].get_actor_instance()

    f1 = factories['federation.Follow'](approved=True, target=library_actor)
    f2 = factories['federation.Follow'](approved=False, target=library_actor)
    f3 = factories['federation.Follow']()

    mocked_deliver = mocker.patch('funkwhale_api.federation.activity.deliver')
    batch = factories['music.ImportBatch']()
    job1 = factories['music.ImportJob'](
        finished=True, batch=batch)
    job2 = factories['music.ImportJob'](
        finished=True, federation=True, batch=batch)
    job3 = factories['music.ImportJob'](
        status='pending', batch=batch)

    batch.status = 'finished'
    batch.save()
    tasks.import_batch_notify_followers(import_batch_id=batch.pk)

    # only f1 match the requirements to be notified
    # and only job1 is a non federated track with finished import
    expected = {
        '@context': federation_serializers.AP_CONTEXT,
        'actor': library_actor.url,
        'type': 'Create',
        'id': batch.get_federation_url(),
        'to': [f1.actor.url],
        'object': federation_serializers.CollectionSerializer(
            {
                'id': batch.get_federation_url(),
                'items': [job1.track_file],
                'actor': library_actor,
                'item_serializer': federation_serializers.AudioSerializer
            }
        ).data
    }

    mocked_deliver.assert_called_once_with(
        expected,
        on_behalf_of=library_actor,
        to=[f1.actor.url]
    )


def test__do_import_in_place_mbid(factories, tmpfile):
    path = os.path.join(DATA_DIR, 'test.ogg')
    job = factories['music.ImportJob'](
        in_place=True, source='file://{}'.format(path))

    track = factories['music.Track'](mbid=job.mbid)
    tf = tasks._do_import(job, use_acoustid=False)

    assert bool(tf.audio_file) is False
    assert tf.source == 'file://{}'.format(path)
    assert tf.mimetype == 'audio/ogg'
