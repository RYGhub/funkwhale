from django.db import transaction

from rest_framework import serializers

from funkwhale_api.federation import serializers as federation_serializers
from funkwhale_api.music import models as music_models
from funkwhale_api.music import serializers as music_serializers
from funkwhale_api.tags import models as tags_models
from funkwhale_api.tags import serializers as tags_serializers

from . import models


class ChannelCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=music_models.MAX_LENGTHS["ARTIST_NAME"])
    username = serializers.CharField(max_length=music_models.MAX_LENGTHS["ARTIST_NAME"])
    summary = serializers.CharField(max_length=500, allow_blank=True, allow_null=True)
    tags = tags_serializers.TagsListField()

    @transaction.atomic
    def create(self, validated_data):
        artist = music_models.Artist.objects.create(
            attributed_to=validated_data["attributed_to"], name=validated_data["name"]
        )
        if validated_data.get("tags", []):
            tags_models.set_tags(artist, *validated_data["tags"])

        channel = models.Channel(
            artist=artist, attributed_to=validated_data["attributed_to"]
        )

        channel.actor = models.generate_actor(
            validated_data["username"],
            summary=validated_data["summary"],
            name=validated_data["name"],
        )

        channel.library = music_models.Library.objects.create(
            name=channel.actor.preferred_username,
            privacy_level="everyone",
            actor=validated_data["attributed_to"],
        )
        channel.save()
        return channel

    def to_representation(self, obj):
        return ChannelSerializer(obj).data


class ChannelUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=music_models.MAX_LENGTHS["ARTIST_NAME"])
    summary = serializers.CharField(max_length=500, allow_blank=True, allow_null=True)
    tags = tags_serializers.TagsListField()

    @transaction.atomic
    def update(self, obj, validated_data):
        if validated_data.get("tags") is not None:
            tags_models.set_tags(obj.artist, *validated_data["tags"])
        actor_update_fields = []

        if "summary" in validated_data:
            actor_update_fields.append(("summary", validated_data["summary"]))
        if "name" in validated_data:
            obj.artist.name = validated_data["name"]
            obj.artist.save(update_fields=["name"])
            actor_update_fields.append(("name", validated_data["name"]))

        if actor_update_fields:
            for field, value in actor_update_fields:
                setattr(obj.actor, field, value)
            obj.actor.save(update_fields=[f for f, _ in actor_update_fields])
        return obj

    def to_representation(self, obj):
        return ChannelSerializer(obj).data


class ChannelSerializer(serializers.ModelSerializer):
    artist = serializers.SerializerMethodField()
    actor = federation_serializers.APIActorSerializer()
    attributed_to = federation_serializers.APIActorSerializer()

    class Meta:
        model = models.Channel
        fields = ["uuid", "artist", "attributed_to", "actor", "creation_date"]

    def get_artist(self, obj):
        return music_serializers.serialize_artist_simple(obj.artist)
