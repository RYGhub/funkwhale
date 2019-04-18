from rest_framework import serializers

from funkwhale_api.common import serializers as common_serializers
from funkwhale_api.music import models as music_models

from . import filters
from . import models
from . import serializers as federation_serializers


class NestedLibraryFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LibraryFollow
        fields = ["creation_date", "uuid", "fid", "approved", "modification_date"]


class LibraryScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = music_models.LibraryScan
        fields = [
            "total_files",
            "processed_files",
            "errored_files",
            "status",
            "creation_date",
            "modification_date",
        ]


class LibrarySerializer(serializers.ModelSerializer):
    actor = federation_serializers.APIActorSerializer()
    uploads_count = serializers.SerializerMethodField()
    latest_scan = serializers.SerializerMethodField()
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
            "uploads_count",
            "privacy_level",
            "follow",
            "latest_scan",
        ]

    def get_uploads_count(self, o):
        return max(getattr(o, "_uploads_count", 0), o.uploads_count)

    def get_follow(self, o):
        try:
            return NestedLibraryFollowSerializer(o._follows[0]).data
        except (AttributeError, IndexError):
            return None

    def get_latest_scan(self, o):
        scan = o.scans.order_by("-creation_date").first()
        if scan:
            return LibraryScanSerializer(scan).data


class LibraryFollowSerializer(serializers.ModelSerializer):
    target = common_serializers.RelatedField("uuid", LibrarySerializer(), required=True)
    actor = serializers.SerializerMethodField()

    class Meta:
        model = models.LibraryFollow
        fields = ["creation_date", "actor", "uuid", "target", "approved"]
        read_only_fields = ["uuid", "actor", "approved", "creation_date"]

    def validate_target(self, v):
        actor = self.context["actor"]
        if v.actor == actor:
            raise serializers.ValidationError("You cannot follow your own library")

        if v.received_follows.filter(actor=actor).exists():
            raise serializers.ValidationError("You are already following this library")
        return v

    def get_actor(self, o):
        return federation_serializers.APIActorSerializer(o.actor).data


def serialize_generic_relation(activity, obj):
    data = {"uuid": obj.uuid, "type": obj._meta.label}
    if data["type"] == "music.Library":
        data["name"] = obj.name
    if data["type"] == "federation.LibraryFollow":
        data["approved"] = obj.approved

    return data


class ActivitySerializer(serializers.ModelSerializer):
    actor = federation_serializers.APIActorSerializer()
    object = serializers.SerializerMethodField()
    target = serializers.SerializerMethodField()
    related_object = serializers.SerializerMethodField()

    class Meta:
        model = models.Activity
        fields = [
            "uuid",
            "fid",
            "actor",
            "payload",
            "object",
            "target",
            "related_object",
            "actor",
            "creation_date",
            "type",
        ]

    def get_object(self, o):
        if o.object:
            return serialize_generic_relation(o, o.object)

    def get_related_object(self, o):
        if o.related_object:
            return serialize_generic_relation(o, o.related_object)

    def get_target(self, o):
        if o.target:
            return serialize_generic_relation(o, o.target)


class InboxItemSerializer(serializers.ModelSerializer):
    activity = ActivitySerializer()

    class Meta:
        model = models.InboxItem
        fields = ["id", "type", "activity", "is_read"]
        read_only_fields = ["id", "type", "activity"]


class InboxItemActionSerializer(common_serializers.ActionSerializer):
    actions = [common_serializers.Action("read", allow_all=True)]
    filterset_class = filters.InboxItemFilter

    def handle_read(self, objects):
        return objects.update(is_read=True)


class FetchSerializer(serializers.ModelSerializer):
    actor = federation_serializers.APIActorSerializer()

    class Meta:
        model = models.Fetch
        fields = [
            "id",
            "url",
            "actor",
            "status",
            "detail",
            "creation_date",
            "fetch_date",
        ]
