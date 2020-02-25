from django.conf import settings
from django.db import transaction

from rest_framework import serializers

from django.templatetags.static import static

from funkwhale_api.common import serializers as common_serializers
from funkwhale_api.common import utils as common_utils
from funkwhale_api.common import locales
from funkwhale_api.common import preferences
from funkwhale_api.federation import models as federation_models
from funkwhale_api.federation import serializers as federation_serializers
from funkwhale_api.federation import utils as federation_utils
from funkwhale_api.music import models as music_models
from funkwhale_api.music import serializers as music_serializers
from funkwhale_api.tags import models as tags_models
from funkwhale_api.tags import serializers as tags_serializers
from funkwhale_api.users import serializers as users_serializers

from . import categories
from . import models


class ChannelMetadataSerializer(serializers.Serializer):
    itunes_category = serializers.ChoiceField(
        choices=categories.ITUNES_CATEGORIES, required=True
    )
    itunes_subcategory = serializers.CharField(required=False, allow_null=True)
    language = serializers.ChoiceField(required=True, choices=locales.ISO_639_CHOICES)
    copyright = serializers.CharField(required=False, allow_null=True, max_length=255)
    owner_name = serializers.CharField(required=False, allow_null=True, max_length=255)
    owner_email = serializers.EmailField(required=False, allow_null=True)
    explicit = serializers.BooleanField(required=False)

    def validate(self, validated_data):
        validated_data = super().validate(validated_data)
        subcategory = self._validate_itunes_subcategory(
            validated_data["itunes_category"], validated_data.get("itunes_subcategory")
        )
        if subcategory:
            validated_data["itunes_subcategory"] = subcategory
        return validated_data

    def _validate_itunes_subcategory(self, parent, child):
        if not child:
            return

        if child not in categories.ITUNES_CATEGORIES[parent]:
            raise serializers.ValidationError(
                '"{}" is not a valid subcategory for "{}"'.format(child, parent)
            )

        return child


class ChannelCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=music_models.MAX_LENGTHS["ARTIST_NAME"])
    username = serializers.CharField(
        max_length=music_models.MAX_LENGTHS["ARTIST_NAME"],
        validators=[users_serializers.ASCIIUsernameValidator()],
    )
    description = common_serializers.ContentSerializer(allow_null=True)
    tags = tags_serializers.TagsListField()
    content_category = serializers.ChoiceField(
        choices=music_models.ARTIST_CONTENT_CATEGORY_CHOICES
    )
    metadata = serializers.DictField(required=False)
    cover = music_serializers.COVER_WRITE_FIELD

    def validate(self, validated_data):
        existing_channels = self.context["actor"].owned_channels.count()
        if existing_channels >= preferences.get("audio__max_channels"):
            raise serializers.ValidationError(
                "You have reached the maximum amount of allowed channels"
            )
        validated_data = super().validate(validated_data)
        metadata = validated_data.pop("metadata", {})
        if validated_data["content_category"] == "podcast":
            metadata_serializer = ChannelMetadataSerializer(data=metadata)
            metadata_serializer.is_valid(raise_exception=True)
            metadata = metadata_serializer.validated_data
        validated_data["metadata"] = metadata
        return validated_data

    def validate_username(self, value):
        if value.lower() in [n.lower() for n in settings.ACCOUNT_USERNAME_BLACKLIST]:
            raise serializers.ValidationError("This username is already taken")

        matching = federation_models.Actor.objects.local().filter(
            preferred_username__iexact=value
        )
        if matching.exists():
            raise serializers.ValidationError("This username is already taken")
        return value

    @transaction.atomic
    def create(self, validated_data):
        from . import views

        cover = validated_data.pop("cover", None)
        description = validated_data.get("description")
        artist = music_models.Artist.objects.create(
            attributed_to=validated_data["attributed_to"],
            name=validated_data["name"],
            content_category=validated_data["content_category"],
            attachment_cover=cover,
        )
        common_utils.attach_content(artist, "description", description)

        if validated_data.get("tags", []):
            tags_models.set_tags(artist, *validated_data["tags"])

        channel = models.Channel(
            artist=artist,
            attributed_to=validated_data["attributed_to"],
            metadata=validated_data["metadata"],
        )
        channel.actor = models.generate_actor(
            validated_data["username"], name=validated_data["name"],
        )

        channel.library = music_models.Library.objects.create(
            name=channel.actor.preferred_username,
            privacy_level="everyone",
            actor=validated_data["attributed_to"],
        )
        channel.save()
        channel = views.ChannelViewSet.queryset.get(pk=channel.pk)
        return channel

    def to_representation(self, obj):
        return ChannelSerializer(obj, context=self.context).data


NOOP = object()


class ChannelUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=music_models.MAX_LENGTHS["ARTIST_NAME"])
    description = common_serializers.ContentSerializer(allow_null=True)
    tags = tags_serializers.TagsListField()
    content_category = serializers.ChoiceField(
        choices=music_models.ARTIST_CONTENT_CATEGORY_CHOICES
    )
    metadata = serializers.DictField(required=False)
    cover = music_serializers.COVER_WRITE_FIELD

    def validate(self, validated_data):
        validated_data = super().validate(validated_data)
        require_metadata_validation = False
        new_content_category = validated_data.get("content_category")
        metadata = validated_data.pop("metadata", NOOP)
        if (
            new_content_category == "podcast"
            and self.instance.artist.content_category != "postcast"
        ):
            # updating channel, setting as podcast
            require_metadata_validation = True
        elif self.instance.artist.content_category == "postcast" and metadata != NOOP:
            # channel is podcast, and metadata was updated
            require_metadata_validation = True
        else:
            metadata = self.instance.metadata

        if require_metadata_validation:
            metadata_serializer = ChannelMetadataSerializer(data=metadata)
            metadata_serializer.is_valid(raise_exception=True)
            metadata = metadata_serializer.validated_data

        validated_data["metadata"] = metadata
        return validated_data

    @transaction.atomic
    def update(self, obj, validated_data):
        if validated_data.get("tags") is not None:
            tags_models.set_tags(obj.artist, *validated_data["tags"])
        actor_update_fields = []
        artist_update_fields = []

        obj.metadata = validated_data["metadata"]
        obj.save(update_fields=["metadata"])

        if "description" in validated_data:
            description_obj = common_utils.attach_content(
                obj.artist, "description", validated_data["description"]
            )
            if description_obj:
                actor_update_fields.append(("summary", description_obj.rendered))

        if "name" in validated_data:
            actor_update_fields.append(("name", validated_data["name"]))
            artist_update_fields.append(("name", validated_data["name"]))

        if "content_category" in validated_data:
            artist_update_fields.append(
                ("content_category", validated_data["content_category"])
            )

        if "cover" in validated_data:
            artist_update_fields.append(("attachment_cover", validated_data["cover"]))

        if actor_update_fields:
            for field, value in actor_update_fields:
                setattr(obj.actor, field, value)
            obj.actor.save(update_fields=[f for f, _ in actor_update_fields])

        if artist_update_fields:
            for field, value in artist_update_fields:
                setattr(obj.artist, field, value)
            obj.artist.save(update_fields=[f for f, _ in artist_update_fields])

        return obj

    def to_representation(self, obj):
        return ChannelSerializer(obj, context=self.context).data


class ChannelSerializer(serializers.ModelSerializer):
    artist = serializers.SerializerMethodField()
    actor = federation_serializers.APIActorSerializer()
    attributed_to = federation_serializers.APIActorSerializer()
    rss_url = serializers.CharField(source="get_rss_url")

    class Meta:
        model = models.Channel
        fields = [
            "uuid",
            "artist",
            "attributed_to",
            "actor",
            "creation_date",
            "metadata",
            "rss_url",
        ]

    def get_artist(self, obj):
        return music_serializers.serialize_artist_simple(obj.artist)

    def to_representation(self, obj):
        data = super().to_representation(obj)
        if self.context.get("subscriptions_count"):
            data["subscriptions_count"] = self.get_subscriptions_count(obj)
        return data

    def get_subscriptions_count(self, obj):
        return obj.actor.received_follows.exclude(approved=False).count()


class SubscriptionSerializer(serializers.Serializer):
    approved = serializers.BooleanField(read_only=True)
    fid = serializers.URLField(read_only=True)
    uuid = serializers.UUIDField(read_only=True)
    creation_date = serializers.DateTimeField(read_only=True)

    def to_representation(self, obj):
        data = super().to_representation(obj)
        data["channel"] = ChannelSerializer(obj.target.channel).data
        return data


# RSS related stuff
# https://github.com/simplepie/simplepie-ng/wiki/Spec:-iTunes-Podcast-RSS
# is extremely useful


def rss_date(dt):
    return dt.strftime("%a, %d %b %Y %H:%M:%S %z")


def rss_duration(seconds):
    if not seconds:
        return "00:00:00"
    full_hours = seconds // 3600
    full_minutes = (seconds - (full_hours * 3600)) // 60
    remaining_seconds = seconds - (full_hours * 3600) - (full_minutes * 60)
    return "{}:{}:{}".format(
        str(full_hours).zfill(2),
        str(full_minutes).zfill(2),
        str(remaining_seconds).zfill(2),
    )


def rss_serialize_item(upload):
    data = {
        "title": [{"value": upload.track.title}],
        "itunes:title": [{"value": upload.track.title}],
        "guid": [{"cdata_value": str(upload.uuid), "isPermalink": "false"}],
        "pubDate": [{"value": rss_date(upload.creation_date)}],
        "itunes:duration": [{"value": rss_duration(upload.duration)}],
        "itunes:explicit": [{"value": "no"}],
        "itunes:episodeType": [{"value": "full"}],
        "itunes:season": [{"value": upload.track.disc_number or 1}],
        "itunes:episode": [{"value": upload.track.position or 1}],
        "link": [{"value": federation_utils.full_url(upload.track.get_absolute_url())}],
        "enclosure": [
            {
                # we enforce MP3, since it's the only format supported everywhere
                "url": federation_utils.full_url(upload.get_listen_url(to="mp3")),
                "length": upload.size or 0,
                "type": "audio/mpeg",
            }
        ],
    }
    if upload.track.description:
        data["itunes:subtitle"] = [{"value": upload.track.description.truncate(255)}]
        data["itunes:summary"] = [{"cdata_value": upload.track.description.rendered}]
        data["description"] = [{"value": upload.track.description.as_plain_text}]

    if upload.track.attachment_cover:
        data["itunes:image"] = [
            {"href": upload.track.attachment_cover.download_url_original}
        ]

    tagged_items = getattr(upload.track, "_prefetched_tagged_items", [])
    if tagged_items:
        data["itunes:keywords"] = [
            {"value": " ".join([ti.tag.name for ti in tagged_items])}
        ]

    return data


def rss_serialize_channel(channel):
    metadata = channel.metadata or {}
    explicit = metadata.get("explicit", False)
    copyright = metadata.get("copyright", "All rights reserved")
    owner_name = metadata.get("owner_name", channel.attributed_to.display_name)
    owner_email = metadata.get("owner_email")
    itunes_category = metadata.get("itunes_category")
    itunes_subcategory = metadata.get("itunes_subcategory")
    language = metadata.get("language")

    data = {
        "title": [{"value": channel.artist.name}],
        "copyright": [{"value": copyright}],
        "itunes:explicit": [{"value": "no" if not explicit else "yes"}],
        "itunes:author": [{"value": owner_name}],
        "itunes:owner": [{"itunes:name": [{"value": owner_name}]}],
        "itunes:type": [{"value": "episodic"}],
        "link": [{"value": channel.get_absolute_url()}],
        "atom:link": [
            {
                "href": channel.get_rss_url(),
                "rel": "self",
                "type": "application/rss+xml",
            }
        ],
    }
    if language:
        data["language"] = [{"value": language}]

    if owner_email:
        data["itunes:owner"][0]["itunes:email"] = [{"value": owner_email}]

    if itunes_category:
        node = {"text": itunes_category}
        if itunes_subcategory:
            node["itunes:category"] = [{"text": itunes_subcategory}]
        data["itunes:category"] = [node]

    if channel.artist.description:
        data["itunes:subtitle"] = [{"value": channel.artist.description.truncate(255)}]
        data["itunes:summary"] = [{"cdata_value": channel.artist.description.rendered}]
        data["description"] = [{"value": channel.artist.description.as_plain_text}]

    if channel.artist.attachment_cover:
        data["itunes:image"] = [
            {"href": channel.artist.attachment_cover.download_url_original}
        ]
    else:
        placeholder_url = federation_utils.full_url(
            static("images/podcasts-cover-placeholder.png")
        )
        data["itunes:image"] = [{"href": placeholder_url}]

    tagged_items = getattr(channel.artist, "_prefetched_tagged_items", [])

    if tagged_items:
        data["itunes:keywords"] = [
            {"value": " ".join([ti.tag.name for ti in tagged_items])}
        ]

    return data


def rss_serialize_channel_full(channel, uploads):
    channel_data = rss_serialize_channel(channel)
    channel_data["item"] = [rss_serialize_item(upload) for upload in uploads]
    return {"channel": channel_data}
