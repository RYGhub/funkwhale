from rest_framework import serializers

from funkwhale_api.common import serializers as common_serializers
from funkwhale_api.music import models as music_models

from . import serializers as federation_serializers
from . import models


class NestedLibraryFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LibraryFollow
        fields = ["creation_date", "uuid", "fid", "approved", "modification_date"]


class LibrarySerializer(serializers.ModelSerializer):
    actor = federation_serializers.APIActorSerializer()
    files_count = serializers.SerializerMethodField()
    follow = serializers.SerializerMethodField()

    class Meta:
        model = music_models.Library
        fields = [
            "fid",
            "uuid",
            "actor",
            "name",
            "description",
            "creation_date",
            "files_count",
            "privacy_level",
            "follow",
        ]

    def get_files_count(self, o):
        return max(getattr(o, "_files_count", 0), o.files_count)

    def get_follow(self, o):
        try:
            return NestedLibraryFollowSerializer(o._follows[0]).data
        except (AttributeError, IndexError):
            return None


class LibraryFollowSerializer(serializers.ModelSerializer):
    target = common_serializers.RelatedField("uuid", LibrarySerializer(), required=True)

    class Meta:
        model = models.LibraryFollow
        fields = ["creation_date", "uuid", "target", "approved"]
        read_only_fields = ["uuid", "approved", "creation_date"]

    def validate_target(self, v):
        actor = self.context["actor"]
        if v.received_follows.filter(actor=actor).exists():
            raise serializers.ValidationError("You are already following this library")
        return v
