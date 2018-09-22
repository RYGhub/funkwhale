from django.db import transaction
from rest_framework import serializers
from taggit.models import Tag
from versatileimagefield.serializers import VersatileImageFieldSerializer

from funkwhale_api.activity import serializers as activity_serializers
from funkwhale_api.common import serializers as common_serializers
from funkwhale_api.common import utils as common_utils
from funkwhale_api.federation import routes

from . import filters, models, tasks


cover_field = VersatileImageFieldSerializer(allow_null=True, sizes="square")


class ArtistAlbumSerializer(serializers.ModelSerializer):
    tracks_count = serializers.SerializerMethodField()
    cover = cover_field
    is_playable = serializers.SerializerMethodField()

    class Meta:
        model = models.Album
        fields = (
            "id",
            "mbid",
            "title",
            "artist",
            "release_date",
            "cover",
            "creation_date",
            "tracks_count",
            "is_playable",
        )

    def get_tracks_count(self, o):
        return o._tracks_count

    def get_is_playable(self, obj):
        try:
            return bool(obj.is_playable_by_actor)
        except AttributeError:
            return None


class ArtistWithAlbumsSerializer(serializers.ModelSerializer):
    albums = ArtistAlbumSerializer(many=True, read_only=True)

    class Meta:
        model = models.Artist
        fields = ("id", "mbid", "name", "creation_date", "albums")


class ArtistSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Artist
        fields = ("id", "mbid", "name", "creation_date")


class AlbumTrackSerializer(serializers.ModelSerializer):
    artist = ArtistSimpleSerializer(read_only=True)
    is_playable = serializers.SerializerMethodField()
    listen_url = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()

    class Meta:
        model = models.Track
        fields = (
            "id",
            "mbid",
            "title",
            "album",
            "artist",
            "creation_date",
            "position",
            "is_playable",
            "listen_url",
            "duration",
        )

    def get_is_playable(self, obj):
        try:
            return bool(obj.is_playable_by_actor)
        except AttributeError:
            return None

    def get_listen_url(self, obj):
        return obj.listen_url

    def get_duration(self, obj):
        try:
            return obj.duration
        except AttributeError:
            return None


class AlbumSerializer(serializers.ModelSerializer):
    tracks = serializers.SerializerMethodField()
    artist = ArtistSimpleSerializer(read_only=True)
    cover = cover_field
    is_playable = serializers.SerializerMethodField()

    class Meta:
        model = models.Album
        fields = (
            "id",
            "mbid",
            "title",
            "artist",
            "tracks",
            "release_date",
            "cover",
            "creation_date",
            "is_playable",
        )

    def get_tracks(self, o):
        ordered_tracks = sorted(
            o.tracks.all(),
            key=lambda v: (v.position, v.title) if v.position else (99999, v.title),
        )
        return AlbumTrackSerializer(ordered_tracks, many=True).data

    def get_is_playable(self, obj):
        try:
            return any([bool(t.is_playable_by_actor) for t in obj.tracks.all()])
        except AttributeError:
            return None


class TrackAlbumSerializer(serializers.ModelSerializer):
    artist = ArtistSimpleSerializer(read_only=True)
    cover = cover_field

    class Meta:
        model = models.Album
        fields = (
            "id",
            "mbid",
            "title",
            "artist",
            "release_date",
            "cover",
            "creation_date",
        )


class TrackSerializer(serializers.ModelSerializer):
    artist = ArtistSimpleSerializer(read_only=True)
    album = TrackAlbumSerializer(read_only=True)
    lyrics = serializers.SerializerMethodField()
    is_playable = serializers.SerializerMethodField()
    listen_url = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    bitrate = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    mimetype = serializers.SerializerMethodField()

    class Meta:
        model = models.Track
        fields = (
            "id",
            "mbid",
            "title",
            "album",
            "artist",
            "creation_date",
            "position",
            "lyrics",
            "is_playable",
            "listen_url",
            "duration",
            "bitrate",
            "size",
            "mimetype",
        )

    def get_lyrics(self, obj):
        return obj.get_lyrics_url()

    def get_listen_url(self, obj):
        return obj.listen_url

    def get_is_playable(self, obj):
        try:
            return bool(obj.is_playable_by_actor)
        except AttributeError:
            return None

    def get_duration(self, obj):
        try:
            return obj.duration
        except AttributeError:
            return None

    def get_bitrate(self, obj):
        try:
            return obj.bitrate
        except AttributeError:
            return None

    def get_size(self, obj):
        try:
            return obj.size
        except AttributeError:
            return None

    def get_mimetype(self, obj):
        try:
            return obj.mimetype
        except AttributeError:
            return None


class LibraryForOwnerSerializer(serializers.ModelSerializer):
    uploads_count = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()

    class Meta:
        model = models.Library
        fields = [
            "uuid",
            "fid",
            "name",
            "description",
            "privacy_level",
            "uploads_count",
            "size",
            "creation_date",
        ]
        read_only_fields = ["fid", "uuid", "creation_date", "actor"]

    def get_uploads_count(self, o):
        return getattr(o, "_uploads_count", o.uploads_count)

    def get_size(self, o):
        return getattr(o, "_size", 0)


class UploadSerializer(serializers.ModelSerializer):
    track = TrackSerializer(required=False, allow_null=True)
    library = common_serializers.RelatedField(
        "uuid",
        LibraryForOwnerSerializer(),
        required=True,
        filters=lambda context: {"actor": context["user"].actor},
    )

    class Meta:
        model = models.Upload
        fields = [
            "uuid",
            "filename",
            "creation_date",
            "mimetype",
            "track",
            "library",
            "duration",
            "mimetype",
            "bitrate",
            "size",
            "import_date",
            "import_status",
        ]

        read_only_fields = [
            "uuid",
            "creation_date",
            "duration",
            "mimetype",
            "bitrate",
            "size",
            "track",
            "import_date",
            "import_status",
        ]


class UploadForOwnerSerializer(UploadSerializer):
    class Meta(UploadSerializer.Meta):
        fields = UploadSerializer.Meta.fields + [
            "import_details",
            "import_metadata",
            "import_reference",
            "metadata",
            "source",
            "audio_file",
        ]
        write_only_fields = ["audio_file"]
        read_only_fields = UploadSerializer.Meta.read_only_fields + [
            "import_details",
            "import_metadata",
            "metadata",
        ]

    def to_representation(self, obj):
        r = super().to_representation(obj)
        if "audio_file" in r:
            del r["audio_file"]
        return r

    def validate(self, validated_data):
        if "audio_file" in validated_data:
            self.validate_upload_quota(validated_data["audio_file"])

        return super().validate(validated_data)

    def validate_upload_quota(self, f):
        quota_status = self.context["user"].get_quota_status()
        if (f.size / 1000 / 1000) > quota_status["remaining"]:
            raise serializers.ValidationError("upload_quota_reached")

        return f


class UploadActionSerializer(common_serializers.ActionSerializer):
    actions = [
        common_serializers.Action("delete", allow_all=True),
        common_serializers.Action("relaunch_import", allow_all=True),
    ]
    filterset_class = filters.UploadFilter
    pk_field = "uuid"

    @transaction.atomic
    def handle_delete(self, objects):
        libraries = sorted(set(objects.values_list("library", flat=True)))
        for id in libraries:
            # we group deletes by library for easier federation
            uploads = objects.filter(library__pk=id).select_related("library__actor")
            for chunk in common_utils.chunk_queryset(uploads, 100):
                routes.outbox.dispatch(
                    {"type": "Delete", "object": {"type": "Audio"}},
                    context={"uploads": chunk},
                )

        return objects.delete()

    @transaction.atomic
    def handle_relaunch_import(self, objects):
        qs = objects.exclude(import_status="finished")
        pks = list(qs.values_list("id", flat=True))
        qs.update(import_status="pending")
        for pk in pks:
            common_utils.on_commit(tasks.import_upload.delay, upload_id=pk)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class SimpleAlbumSerializer(serializers.ModelSerializer):
    cover = cover_field

    class Meta:
        model = models.Album
        fields = ("id", "mbid", "title", "release_date", "cover")


class LyricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Lyrics
        fields = ("id", "work", "content", "content_rendered")


class TrackActivitySerializer(activity_serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    name = serializers.CharField(source="title")
    artist = serializers.CharField(source="artist.name")
    album = serializers.CharField(source="album.title")

    class Meta:
        model = models.Track
        fields = ["id", "local_id", "name", "type", "artist", "album"]

    def get_type(self, obj):
        return "Audio"
