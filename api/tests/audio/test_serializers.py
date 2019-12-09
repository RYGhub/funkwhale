from funkwhale_api.audio import serializers
from funkwhale_api.federation import serializers as federation_serializers
from funkwhale_api.music import serializers as music_serializers


def test_channel_serializer_create(factories):
    attributed_to = factories["federation.Actor"](local=True)

    data = {
        # TODO: cover
        "name": "My channel",
        "username": "mychannel",
        "summary": "This is my channel",
        "tags": ["hello", "world"],
    }

    serializer = serializers.ChannelCreateSerializer(data=data)
    assert serializer.is_valid(raise_exception=True) is True

    channel = serializer.save(attributed_to=attributed_to)

    assert channel.artist.name == data["name"]
    assert channel.artist.attributed_to == attributed_to
    assert (
        sorted(channel.artist.tagged_items.values_list("tag__name", flat=True))
        == data["tags"]
    )
    assert channel.attributed_to == attributed_to
    assert channel.actor.summary == data["summary"]
    assert channel.actor.preferred_username == data["username"]
    assert channel.actor.name == data["name"]
    assert channel.library.privacy_level == "everyone"
    assert channel.library.actor == attributed_to


def test_channel_serializer_update(factories):
    channel = factories["audio.Channel"](artist__set_tags=["rock"])

    data = {
        # TODO: cover
        "name": "My channel",
        "summary": "This is my channel",
        "tags": ["hello", "world"],
    }

    serializer = serializers.ChannelUpdateSerializer(channel, data=data)
    assert serializer.is_valid(raise_exception=True) is True

    serializer.save()
    channel.refresh_from_db()

    assert channel.artist.name == data["name"]
    assert (
        sorted(channel.artist.tagged_items.values_list("tag__name", flat=True))
        == data["tags"]
    )
    assert channel.actor.summary == data["summary"]
    assert channel.actor.name == data["name"]


def test_channel_serializer_representation(factories, to_api_date):
    channel = factories["audio.Channel"]()

    expected = {
        "artist": music_serializers.serialize_artist_simple(channel.artist),
        "uuid": str(channel.uuid),
        "creation_date": to_api_date(channel.creation_date),
        "actor": federation_serializers.APIActorSerializer(channel.actor).data,
        "attributed_to": federation_serializers.APIActorSerializer(
            channel.attributed_to
        ).data,
    }

    assert serializers.ChannelSerializer(channel).data == expected
