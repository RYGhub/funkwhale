from django.db import transaction
from rest_framework import serializers

from funkwhale_api.common import serializers as common_serializers
from funkwhale_api.music import models as music_models
from funkwhale_api.users import models as users_models

from . import filters


class ManageTrackFileArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = music_models.Artist
        fields = ["id", "mbid", "creation_date", "name"]


class ManageTrackFileAlbumSerializer(serializers.ModelSerializer):
    artist = ManageTrackFileArtistSerializer()

    class Meta:
        model = music_models.Album
        fields = (
            "id",
            "mbid",
            "title",
            "artist",
            "release_date",
            "cover",
            "creation_date",
        )


class ManageTrackFileTrackSerializer(serializers.ModelSerializer):
    artist = ManageTrackFileArtistSerializer()
    album = ManageTrackFileAlbumSerializer()

    class Meta:
        model = music_models.Track
        fields = ("id", "mbid", "title", "album", "artist", "creation_date", "position")


class ManageTrackFileSerializer(serializers.ModelSerializer):
    track = ManageTrackFileTrackSerializer()

    class Meta:
        model = music_models.TrackFile
        fields = (
            "id",
            "path",
            "source",
            "filename",
            "mimetype",
            "track",
            "duration",
            "mimetype",
            "bitrate",
            "size",
            "path",
            "library_track",
        )


class ManageTrackFileActionSerializer(common_serializers.ActionSerializer):
    actions = ["delete"]
    dangerous_actions = ["delete"]
    filterset_class = filters.ManageTrackFileFilterSet

    @transaction.atomic
    def handle_delete(self, objects):
        return objects.delete()


class PermissionsSerializer(serializers.Serializer):
    def to_representation(self, o):
        return o.get_permissions(defaults=self.context.get("default_permissions"))

    def to_internal_value(self, o):
        return {"permissions": o}


class ManageUserSerializer(serializers.ModelSerializer):
    permissions = PermissionsSerializer(source="*")

    class Meta:
        model = users_models.User
        fields = (
            "id",
            "username",
            "email",
            "name",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
            "last_activity",
            "permissions",
            "privacy_level",
        )
        read_only_fields = [
            "id",
            "email",
            "privacy_level",
            "username",
            "date_joined",
            "last_activity",
        ]

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        permissions = validated_data.pop("permissions", {})
        if permissions:
            for p, value in permissions.items():
                setattr(instance, "permission_{}".format(p), value)
            instance.save(
                update_fields=["permission_{}".format(p) for p in permissions.keys()]
            )
        return instance
