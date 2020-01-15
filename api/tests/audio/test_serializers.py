from funkwhale_api.audio import serializers
from funkwhale_api.common import serializers as common_serializers
from funkwhale_api.common import utils as common_utils
from funkwhale_api.federation import serializers as federation_serializers
from funkwhale_api.music import serializers as music_serializers


def test_channel_serializer_create(factories):
    attributed_to = factories["federation.Actor"](local=True)

    data = {
        # TODO: cover
        "name": "My channel",
        "username": "mychannel",
        "description": {"text": "This is my channel", "content_type": "text/markdown"},
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
    assert channel.artist.description.text == data["description"]["text"]
    assert (
        channel.artist.description.content_type == data["description"]["content_type"]
    )
    assert channel.attributed_to == attributed_to
    assert channel.actor.summary == common_utils.render_html(
        data["description"]["text"], "text/markdown"
    )
    assert channel.actor.preferred_username == data["username"]
    assert channel.actor.name == data["name"]
    assert channel.library.privacy_level == "everyone"
    assert channel.library.actor == attributed_to


def test_channel_serializer_update(factories):
    channel = factories["audio.Channel"](artist__set_tags=["rock"])

    data = {
        # TODO: cover
        "name": "My channel",
        "description": {"text": "This is my channel", "content_type": "text/markdown"},
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
    assert channel.actor.summary == common_utils.render_html(
        data["description"]["text"], "text/markdown"
    )
    assert channel.artist.description.text == data["description"]["text"]
    assert channel.artist.description.content_type == "text/markdown"
    assert channel.actor.name == data["name"]


def test_channel_serializer_representation(factories, to_api_date):
    content = factories["common.Content"]()
    channel = factories["audio.Channel"](artist__description=content)

    expected = {
        "artist": music_serializers.serialize_artist_simple(channel.artist),
        "uuid": str(channel.uuid),
        "creation_date": to_api_date(channel.creation_date),
        "actor": federation_serializers.APIActorSerializer(channel.actor).data,
        "attributed_to": federation_serializers.APIActorSerializer(
            channel.attributed_to
        ).data,
    }
    expected["artist"]["description"] = common_serializers.ContentSerializer(
        content
    ).data

    assert serializers.ChannelSerializer(channel).data == expected
