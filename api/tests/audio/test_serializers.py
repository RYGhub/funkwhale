import datetime

import pytest
import pytz

from django.templatetags.static import static

from funkwhale_api.audio import serializers
from funkwhale_api.common import serializers as common_serializers
from funkwhale_api.common import utils as common_utils
from funkwhale_api.federation import serializers as federation_serializers
from funkwhale_api.federation import utils as federation_utils
from funkwhale_api.music import serializers as music_serializers


def test_channel_serializer_create(factories, mocker):
    attributed_to = factories["federation.Actor"](local=True)
    attachment = factories["common.Attachment"](actor=attributed_to)
    request = mocker.Mock(user=mocker.Mock(actor=attributed_to))
    data = {
        "name": "My channel",
        "username": "mychannel",
        "description": {"text": "This is my channel", "content_type": "text/markdown"},
        "tags": ["hello", "world"],
        "content_category": "other",
        "cover": attachment.uuid,
    }

    serializer = serializers.ChannelCreateSerializer(
        data=data, context={"actor": attributed_to, "request": request}
    )
    assert serializer.is_valid(raise_exception=True) is True

    channel = serializer.save(attributed_to=attributed_to)

    assert channel.artist.name == data["name"]
    assert channel.artist.attributed_to == attributed_to
    assert (
        sorted(channel.artist.tagged_items.values_list("tag__name", flat=True))
        == data["tags"]
    )
    assert channel.artist.description.text == data["description"]["text"]
    assert channel.artist.attachment_cover == attachment
    assert channel.artist.content_category == data["content_category"]
    assert (
        channel.artist.description.content_type == data["description"]["content_type"]
    )
    assert channel.attributed_to == attributed_to
    assert channel.actor.preferred_username == data["username"]
    assert channel.actor.name == data["name"]
    assert channel.library.privacy_level == "everyone"
    assert channel.library.actor == attributed_to


def test_channel_serializer_create_honor_max_channels_setting(factories, preferences):
    preferences["audio__max_channels"] = 1
    attributed_to = factories["federation.Actor"](local=True)
    factories["audio.Channel"](attributed_to=attributed_to)
    data = {
        "name": "My channel",
        "username": "mychannel",
        "description": {"text": "This is my channel", "content_type": "text/markdown"},
        "tags": ["hello", "world"],
        "content_category": "other",
    }

    serializer = serializers.ChannelCreateSerializer(
        data=data, context={"actor": attributed_to}
    )
    with pytest.raises(serializers.serializers.ValidationError, match=r".*max.*"):
        assert serializer.is_valid(raise_exception=True)


def test_channel_serializer_create_validates_username_uniqueness(factories):
    attributed_to = factories["federation.Actor"](local=True)
    data = {
        "name": "My channel",
        "username": attributed_to.preferred_username.upper(),
        "description": {"text": "This is my channel", "content_type": "text/markdown"},
        "tags": ["hello", "world"],
        "content_category": "other",
    }

    serializer = serializers.ChannelCreateSerializer(
        data=data, context={"actor": attributed_to}
    )
    with pytest.raises(
        serializers.serializers.ValidationError, match=r".*username is already taken.*"
    ):
        assert serializer.is_valid(raise_exception=True)


def test_channel_serializer_create_validates_username_chars(factories):
    attributed_to = factories["federation.Actor"](local=True)
    data = {
        "name": "My channel",
        "username": "hello world",
        "description": {"text": "This is my channel", "content_type": "text/markdown"},
        "tags": ["hello", "world"],
        "content_category": "other",
    }

    serializer = serializers.ChannelCreateSerializer(
        data=data, context={"actor": attributed_to}
    )
    with pytest.raises(
        serializers.serializers.ValidationError, match=r".*Enter a valid username.*"
    ):
        assert serializer.is_valid(raise_exception=True)


def test_channel_serializer_create_validates_blacklisted_username(factories, settings):
    settings.ACCOUNT_USERNAME_BLACKLIST = ["forBidden"]
    attributed_to = factories["federation.Actor"](local=True)
    data = {
        "name": "My channel",
        "username": "FORBIDDEN",
        "description": {"text": "This is my channel", "content_type": "text/markdown"},
        "tags": ["hello", "world"],
        "content_category": "other",
    }

    serializer = serializers.ChannelCreateSerializer(
        data=data, context={"actor": attributed_to}
    )
    with pytest.raises(
        serializers.serializers.ValidationError, match=r".*username is already taken.*"
    ):
        assert serializer.is_valid(raise_exception=True)


def test_channel_serializer_create_podcast(factories):
    attributed_to = factories["federation.Actor"](local=True)

    data = {
        # TODO: cover
        "name": "My channel",
        "username": "mychannel",
        "description": {"text": "This is my channel", "content_type": "text/markdown"},
        "tags": ["hello", "world"],
        "content_category": "podcast",
        "metadata": {"itunes_category": "Sports", "language": "en"},
    }

    serializer = serializers.ChannelCreateSerializer(
        data=data, context={"actor": attributed_to}
    )
    assert serializer.is_valid(raise_exception=True) is True

    channel = serializer.save(attributed_to=attributed_to)
    assert channel.metadata == data["metadata"]


def test_channel_serializer_update(factories, mocker):
    channel = factories["audio.Channel"](
        artist__set_tags=["rock"], attributed_to__local=True
    )
    attributed_to = channel.attributed_to
    attachment = factories["common.Attachment"](actor=attributed_to)
    request = mocker.Mock(user=mocker.Mock(actor=attributed_to))
    data = {
        "name": "My channel",
        "description": {"text": "This is my channel", "content_type": "text/markdown"},
        "tags": ["hello", "world"],
        "content_category": "other",
        "cover": attachment.uuid,
    }

    serializer = serializers.ChannelUpdateSerializer(
        channel, data=data, context={"request": request}
    )
    assert serializer.is_valid(raise_exception=True) is True

    serializer.save()
    channel.refresh_from_db()

    assert channel.artist.name == data["name"]
    assert channel.artist.attachment_cover == attachment
    assert channel.artist.content_category == data["content_category"]
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


def test_channel_serializer_update_podcast(factories):
    channel = factories["audio.Channel"](artist__set_tags=["rock"])

    data = {
        # TODO: cover
        "name": "My channel",
        "description": {"text": "This is my channel", "content_type": "text/markdown"},
        "tags": ["hello", "world"],
        "content_category": "podcast",
        "metadata": {"language": "en", "itunes_category": "Sports"},
    }

    serializer = serializers.ChannelUpdateSerializer(channel, data=data)
    assert serializer.is_valid(raise_exception=True) is True

    serializer.save()
    channel.refresh_from_db()

    assert channel.metadata == data["metadata"]


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
        "metadata": {},
        "rss_url": channel.get_rss_url(),
    }
    expected["artist"]["description"] = common_serializers.ContentSerializer(
        content
    ).data

    assert serializers.ChannelSerializer(channel).data == expected


def test_channel_serializer_representation_subscriptions_count(factories, to_api_date):
    channel = factories["audio.Channel"]()
    factories["federation.Follow"](target=channel.actor)
    factories["federation.Follow"](target=channel.actor, approved=False)
    serializer = serializers.ChannelSerializer(
        channel, context={"subscriptions_count": True}
    )
    assert serializer.data["subscriptions_count"] == 1


def test_subscription_serializer(factories, to_api_date):
    subscription = factories["audio.Subscription"]()
    expected = {
        "channel": serializers.ChannelSerializer(subscription.target.channel).data,
        "uuid": str(subscription.uuid),
        "creation_date": to_api_date(subscription.creation_date),
        "approved": subscription.approved,
        "fid": subscription.fid,
    }

    assert serializers.SubscriptionSerializer(subscription).data == expected


def test_rss_item_serializer(factories):
    description = factories["common.Content"]()
    upload = factories["music.Upload"](
        playable=True,
        track__set_tags=["pop", "rock"],
        track__description=description,
        track__disc_number=4,
        track__position=42,
    )
    setattr(
        upload.track,
        "_prefetched_tagged_items",
        upload.track.tagged_items.order_by("tag__name"),
    )
    expected = {
        "title": [{"value": upload.track.title}],
        "itunes:title": [{"value": upload.track.title}],
        "itunes:subtitle": [{"value": description.truncate(255)}],
        "itunes:summary": [{"cdata_value": description.rendered}],
        "description": [{"value": description.as_plain_text}],
        "guid": [{"cdata_value": str(upload.uuid), "isPermalink": "false"}],
        "pubDate": [{"value": serializers.rss_date(upload.creation_date)}],
        "itunes:duration": [{"value": serializers.rss_duration(upload.duration)}],
        "itunes:keywords": [{"value": "pop rock"}],
        "itunes:explicit": [{"value": "no"}],
        "itunes:episodeType": [{"value": "full"}],
        "itunes:season": [{"value": upload.track.disc_number}],
        "itunes:episode": [{"value": upload.track.position}],
        "itunes:image": [{"href": upload.track.attachment_cover.download_url_original}],
        "link": [{"value": federation_utils.full_url(upload.track.get_absolute_url())}],
        "enclosure": [
            {
                "url": federation_utils.full_url(upload.get_listen_url("mp3")),
                "length": upload.size,
                "type": "audio/mpeg",
            }
        ],
    }

    assert serializers.rss_serialize_item(upload) == expected


def test_rss_channel_serializer(factories):
    metadata = {
        "language": "fr",
        "itunes_category": "Parent",
        "itunes_subcategory": "Child",
        "copyright": "Myself",
        "owner_name": "Name",
        "owner_email": "name@domain.com",
        "explicit": True,
    }
    description = factories["common.Content"]()
    channel = factories["audio.Channel"](
        artist__set_tags=["pop", "rock"],
        artist__description=description,
        metadata=metadata,
    )
    setattr(
        channel.artist,
        "_prefetched_tagged_items",
        channel.artist.tagged_items.order_by("tag__name"),
    )

    expected = {
        "title": [{"value": channel.artist.name}],
        "language": [{"value": metadata["language"]}],
        "copyright": [{"value": metadata["copyright"]}],
        "itunes:subtitle": [{"value": description.truncate(255)}],
        "itunes:summary": [{"cdata_value": description.rendered}],
        "description": [{"value": description.as_plain_text}],
        "itunes:keywords": [{"value": "pop rock"}],
        "itunes:category": [
            {
                "text": metadata["itunes_category"],
                "itunes:category": [{"text": metadata["itunes_subcategory"]}],
            }
        ],
        "itunes:explicit": [{"value": "yes"}],
        "itunes:owner": [
            {
                "itunes:name": [{"value": metadata["owner_name"]}],
                "itunes:email": [{"value": metadata["owner_email"]}],
            }
        ],
        "itunes:author": [{"value": metadata["owner_name"]}],
        "itunes:type": [{"value": "episodic"}],
        "itunes:image": [
            {"href": channel.artist.attachment_cover.download_url_original}
        ],
        "link": [{"value": channel.get_absolute_url()}],
        "atom:link": [
            {
                "href": channel.get_rss_url(),
                "rel": "self",
                "type": "application/rss+xml",
            }
        ],
    }

    assert serializers.rss_serialize_channel(channel) == expected


def test_rss_channel_serializer_placeholder_image(factories):
    description = factories["common.Content"]()
    channel = factories["audio.Channel"](
        artist__set_tags=["pop", "rock"],
        artist__description=description,
        artist__attachment_cover=None,
    )
    setattr(
        channel.artist,
        "_prefetched_tagged_items",
        channel.artist.tagged_items.order_by("tag__name"),
    )

    expected = [
        {
            "href": federation_utils.full_url(
                static("images/podcasts-cover-placeholder.png")
            )
        }
    ]

    assert serializers.rss_serialize_channel(channel)["itunes:image"] == expected


def test_serialize_full_channel(factories):
    channel = factories["audio.Channel"]()
    upload1 = factories["music.Upload"](playable=True)
    upload2 = factories["music.Upload"](playable=True)

    expected = serializers.rss_serialize_channel(channel)
    expected["item"] = [
        serializers.rss_serialize_item(upload1),
        serializers.rss_serialize_item(upload2),
    ]
    expected = {"channel": expected}

    result = serializers.rss_serialize_channel_full(
        channel=channel, uploads=[upload1, upload2]
    )

    assert result == expected


@pytest.mark.parametrize(
    "seconds, expected",
    [
        (0, "00:00:00"),
        (None, "00:00:00"),
        (61, "00:01:01"),
        (3601, "01:00:01"),
        (7345, "02:02:25"),
    ],
)
def test_rss_duration(seconds, expected):
    assert serializers.rss_duration(seconds) == expected


@pytest.mark.parametrize(
    "dt, expected",
    [
        (
            datetime.datetime(2020, 1, 30, 6, 0, 49, tzinfo=pytz.UTC),
            "Thu, 30 Jan 2020 06:00:49 +0000",
        ),
    ],
)
def test_rss_date(dt, expected):
    assert serializers.rss_date(dt) == expected


def test_channel_metadata_serializer_validation():
    payload = {
        "language": "fr",
        "copyright": "Me",
        "owner_email": "contact@me.com",
        "owner_name": "Me",
        "itunes_category": "Health & Fitness",
        "itunes_subcategory": "Sexuality",
        "unknown_key": "noop",
    }

    serializer = serializers.ChannelMetadataSerializer(data=payload)

    assert serializer.is_valid(raise_exception=True) is True

    payload.pop("unknown_key")

    assert serializer.validated_data == payload
