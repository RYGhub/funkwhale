from django.db import transaction

from rest_framework import serializers

from funkwhale_api.common import serializers as common_serializers
from funkwhale_api.federation import models as federation_models
from funkwhale_api.music import models as music_models
from funkwhale_api.users import models as users_models

from . import filters


class ManageUploadArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = music_models.Artist
        fields = ["id", "mbid", "creation_date", "name"]


class ManageUploadAlbumSerializer(serializers.ModelSerializer):
    artist = ManageUploadArtistSerializer()

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


class ManageUploadTrackSerializer(serializers.ModelSerializer):
    artist = ManageUploadArtistSerializer()
    album = ManageUploadAlbumSerializer()

    class Meta:
        model = music_models.Track
        fields = ("id", "mbid", "title", "album", "artist", "creation_date", "position")


class ManageUploadSerializer(serializers.ModelSerializer):
    track = ManageUploadTrackSerializer()

    class Meta:
        model = music_models.Upload
        fields = (
            "id",
            "path",
            "source",
            "filename",
            "mimetype",
            "track",
            "duration",
            "mimetype",
            "creation_date",
            "bitrate",
            "size",
            "path",
        )


class ManageUploadActionSerializer(common_serializers.ActionSerializer):
    actions = [common_serializers.Action("delete", allow_all=False)]
    filterset_class = filters.ManageUploadFilterSet

    @transaction.atomic
    def handle_delete(self, objects):
        return objects.delete()


class PermissionsSerializer(serializers.Serializer):
    def to_representation(self, o):
        return o.get_permissions(defaults=self.context.get("default_permissions"))

    def to_internal_value(self, o):
        return {"permissions": o}


class ManageUserSimpleSerializer(serializers.ModelSerializer):
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
            "privacy_level",
            "upload_quota",
        )


class ManageUserSerializer(serializers.ModelSerializer):
    permissions = PermissionsSerializer(source="*")
    upload_quota = serializers.IntegerField(allow_null=True)

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
            "upload_quota",
            "full_username",
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


class ManageInvitationSerializer(serializers.ModelSerializer):
    users = ManageUserSimpleSerializer(many=True, required=False)
    owner = ManageUserSimpleSerializer(required=False)
    code = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = users_models.Invitation
        fields = ("id", "owner", "code", "expiration_date", "creation_date", "users")
        read_only_fields = ["id", "expiration_date", "owner", "creation_date", "users"]

    def validate_code(self, value):
        if not value:
            return value
        if users_models.Invitation.objects.filter(code__iexact=value).exists():
            raise serializers.ValidationError(
                "An invitation with this code already exists"
            )
        return value


class ManageInvitationActionSerializer(common_serializers.ActionSerializer):
    actions = [
        common_serializers.Action(
            "delete", allow_all=False, qs_filter=lambda qs: qs.open()
        )
    ]
    filterset_class = filters.ManageInvitationFilterSet

    @transaction.atomic
    def handle_delete(self, objects):
        return objects.delete()


class ManageDomainSerializer(serializers.ModelSerializer):
    actors_count = serializers.SerializerMethodField()
    outbox_activities_count = serializers.SerializerMethodField()

    class Meta:
        model = federation_models.Domain
        fields = [
            "name",
            "creation_date",
            "actors_count",
            "outbox_activities_count",
            "nodeinfo",
            "nodeinfo_fetch_date",
        ]

    def get_actors_count(self, o):
        return getattr(o, "actors_count", 0)

    def get_outbox_activities_count(self, o):
        return getattr(o, "outbox_activities_count", 0)


class ManageActorSerializer(serializers.ModelSerializer):
    uploads_count = serializers.SerializerMethodField()
    user = ManageUserSerializer()

    class Meta:
        model = federation_models.Actor
        fields = [
            "id",
            "url",
            "fid",
            "preferred_username",
            "full_username",
            "domain",
            "name",
            "summary",
            "type",
            "creation_date",
            "last_fetch_date",
            "inbox_url",
            "outbox_url",
            "shared_inbox_url",
            "manually_approves_followers",
            "uploads_count",
            "user",
        ]

    def get_uploads_count(self, o):
        return getattr(o, "uploads_count", 0)
