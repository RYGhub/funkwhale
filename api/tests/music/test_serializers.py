from funkwhale_api.music import serializers


def test_activity_pub_audio_collection_serializer(factories):
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
