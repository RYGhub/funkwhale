import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core import validators
from django.utils import timezone

from rest_framework import serializers

from funkwhale_api.common import fields as common_fields
from funkwhale_api.common import serializers as common_serializers
from funkwhale_api.music import models as music_models
from funkwhale_api.users import serializers as users_serializers

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


class DomainSerializer(serializers.Serializer):
    name = serializers.CharField()


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
    data = {"type": obj._meta.label}
    if data["type"] == "federation.Actor":
        data["full_username"] = obj.full_username
    else:
        data["uuid"] = obj.uuid

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


FETCH_OBJECT_CONFIG = {
    "artist": {"queryset": music_models.Artist.objects.all()},
    "album": {"queryset": music_models.Album.objects.all()},
    "track": {"queryset": music_models.Track.objects.all()},
    "library": {"queryset": music_models.Library.objects.all(), "id_attr": "uuid"},
    "upload": {"queryset": music_models.Upload.objects.all(), "id_attr": "uuid"},
    "account": {"queryset": models.Actor.objects.all(), "id_attr": "full_username"},
}
FETCH_OBJECT_FIELD = common_fields.GenericRelation(FETCH_OBJECT_CONFIG)


class FetchSerializer(serializers.ModelSerializer):
    actor = federation_serializers.APIActorSerializer(read_only=True)
    object = serializers.CharField(write_only=True)
    force = serializers.BooleanField(default=False, required=False, write_only=True)

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
            "object",
            "force",
        ]
        read_only_fields = [
            "id",
            "url",
            "actor",
            "status",
            "detail",
            "creation_date",
            "fetch_date",
        ]

    def validate_object(self, value):
        # if value is a webginfer lookup, we craft a special url
        if value.startswith("@"):
            value = value.lstrip("@")
        validator = validators.EmailValidator()
        try:
            validator(value)
        except validators.ValidationError:
            return value

        return "webfinger://{}".format(value)

    def create(self, validated_data):
        check_duplicates = not validated_data.get("force", False)
        if check_duplicates:
            # first we check for duplicates
            duplicate = (
                validated_data["actor"]
                .fetches.filter(
                    status="finished",
                    url=validated_data["object"],
                    creation_date__gte=timezone.now()
                    - datetime.timedelta(
                        seconds=settings.FEDERATION_DUPLICATE_FETCH_DELAY
                    ),
                )
                .order_by("-creation_date")
                .first()
            )
            if duplicate:
                return duplicate

        fetch = models.Fetch.objects.create(
            actor=validated_data["actor"], url=validated_data["object"]
        )
        return fetch

    def to_representation(self, obj):
        repr = super().to_representation(obj)
        object_data = None
        if obj.object:
            object_data = FETCH_OBJECT_FIELD.to_representation(obj.object)
        repr["object"] = object_data
        return repr


class FullActorSerializer(serializers.Serializer):
    fid = serializers.URLField()
    url = serializers.URLField()
    domain = serializers.CharField(source="domain_id")
    creation_date = serializers.DateTimeField()
    last_fetch_date = serializers.DateTimeField()
    name = serializers.CharField()
    preferred_username = serializers.CharField()
    full_username = serializers.CharField()
    type = serializers.CharField()
    is_local = serializers.BooleanField()
    is_channel = serializers.SerializerMethodField()
    manually_approves_followers = serializers.BooleanField()
    user = users_serializers.UserBasicSerializer()
    summary = common_serializers.ContentSerializer(source="summary_obj")
    icon = common_serializers.AttachmentSerializer(source="attachment_icon")

    def get_is_channel(self, o):
        try:
            return bool(o.channel)
        except ObjectDoesNotExist:
            return False
