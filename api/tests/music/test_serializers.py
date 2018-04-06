from funkwhale_api.federation import actors
from funkwhale_api.federation import utils as federation_utils
from funkwhale_api.federation.serializers import AP_CONTEXT
from funkwhale_api.music import serializers


def test_activity_pub_audio_collection_serializer_to_import(factories):
    sender = factories['federation.Actor']()

    collection = {
        'id': 'https://batch.import',
        'type': 'Collection',
        'totalItems': 2,
        'items': factories['federation.Audio'].create_batch(size=2)
    }

    serializer = serializers.AudioCollectionImportSerializer(
        data=collection, context={'sender': sender})

    assert serializer.is_valid(raise_exception=True)

    batch = serializer.save()
    jobs = list(batch.jobs.all())

    assert batch.source == 'federation'
    assert batch.federation_source == collection['id']
    assert batch.federation_actor == sender
    assert len(jobs) == 2

    for i, a in enumerate(collection['items']):
        job = jobs[i]
        assert job.federation_source == a['id']
        assert job.source == a['url']['href']
        a['metadata']['mediaType'] = a['url']['mediaType']
        assert job.metadata == a['metadata']


def test_activity_pub_audio_serializer_to_ap(factories):
    tf = factories['music.TrackFile'](mimetype='audio/mp3')
    library = actors.SYSTEM_ACTORS['library'].get_actor_instance()
    expected = {
        '@context': AP_CONTEXT,
        'type': 'Audio',
        'id': tf.get_federation_url(),
        'name': tf.track.full_name,
        'metadata': {
            'artist': tf.track.artist.musicbrainz_url,
            'release': tf.track.album.musicbrainz_url,
            'track': tf.track.musicbrainz_url,
        },
        'url': {
            'href': federation_utils.full_url(tf.path),
            'type': 'Link',
            'mediaType': 'audio/mp3'
        },
        'attributedTo': [
            library.url
        ]
    }

    serializer = serializers.AudioSerializer(tf, context={'actor': library})

    assert serializer.data == expected


def test_activity_pub_audio_collection_serializer_to_ap(factories):
    tf1 = factories['music.TrackFile'](mimetype='audio/mp3')
    tf2 = factories['music.TrackFile'](mimetype='audio/ogg')
    library = actors.SYSTEM_ACTORS['library'].get_actor_instance()
    expected = {
        '@context': AP_CONTEXT,
        'id': 'https://test.id',
        'actor': library.url,
        'totalItems': 2,
        'type': 'Collection',
        'items': [
            serializers.AudioSerializer(
                tf1, context={'actor': library, 'include_ap_context': False}
            ).data,
            serializers.AudioSerializer(
                tf2, context={'actor': library, 'include_ap_context': False}
            ).data,
        ]
    }

    collection = {
        'id': expected['id'],
        'actor': library,
        'items': [tf1, tf2],
    }
    serializer = serializers.AudioCollectionImportSerializer(
        collection, context={'actor': library, 'id': 'https://test.id'})

    assert serializer.data == expected
