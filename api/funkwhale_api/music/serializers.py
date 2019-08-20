import urllib.parse

from django.db import transaction
from django import urls
from django.conf import settings
from rest_framework import serializers
from versatileimagefield.serializers import VersatileImageFieldSerializer

from funkwhale_api.activity import serializers as activity_serializers
from funkwhale_api.common import serializers as common_serializers
from funkwhale_api.common import utils as common_utils
from funkwhale_api.federation import routes
from funkwhale_api.federation import utils as federation_utils
from funkwhale_api.tags.models import Tag

from . import filters, models, tasks


cover_field = VersatileImageFieldSerializer(allow_null=True, sizes="square")


def serialize_attributed_to(self, obj):
    # Import at runtime to avoid a circular import issue
    from funkwhale_api.federation import serializers as federation_serializers

    if not obj.attributed_to_id:
        return

    return federation_serializers.APIActorSerializer(obj.attributed_to).data


class LicenseSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    url = serializers.URLField()
    code = serializers.CharField()
    name = serializers.CharField()
    redistribute = serializers.BooleanField()
    derivative = serializers.BooleanField()
    commercial = serializers.BooleanField()
    attribution = serializers.BooleanField()
    copyleft = serializers.BooleanField()

    def get_id(self, obj):
        return obj["identifiers"][0]


class ArtistAlbumSerializer(serializers.ModelSerializer):
    tracks_count = serializers.SerializerMethodField()
    cover = cover_field
    is_playable = serializers.SerializerMethodField()

    class Meta:
        model = models.Album
        fields = (
            "id",
            "fid",
            "mbid",
            "title",
            "artist",
            "release_date",
            "cover",
            "creation_date",
            "tracks_count",
            "is_playable",
            "is_local",
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
    tags = serializers.SerializerMethodField()
    attributed_to = serializers.SerializerMethodField()
    tracks_count = serializers.SerializerMethodField()

    class Meta:
        model = models.Artist
        fields = (
            "id",
            "fid",
            "mbid",
            "name",
            "creation_date",
            "albums",
            "is_local",
            "tags",
            "attributed_to",
            "tracks_count",
        )

    def get_tags(self, obj):
        tagged_items = getattr(obj, "_prefetched_tagged_items", [])
        return [ti.tag.name for ti in tagged_items]

    get_attributed_to = serialize_attributed_to

    def get_tracks_count(self, o):
        return getattr(o, "_tracks_count", None)


class ArtistSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Artist
        fields = ("id", "fid", "mbid", "name", "creation_date", "is_local")


class AlbumTrackSerializer(serializers.ModelSerializer):
    artist = ArtistSimpleSerializer(read_only=True)
    uploads = serializers.SerializerMethodField()
    listen_url = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()

    class Meta:
        model = models.Track
        fields = (
            "id",
            "fid",
            "mbid",
            "title",
            "album",
            "artist",
            "creation_date",
            "position",
            "disc_number",
            "uploads",
            "listen_url",
            "duration",
            "copyright",
            "license",
            "is_local",
        )

    def get_uploads(self, obj):
        uploads = getattr(obj, "playable_uploads", [])
        return TrackUploadSerializer(uploads, many=True).data

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
    tags = serializers.SerializerMethodField()
    attributed_to = serializers.SerializerMethodField()

    class Meta:
        model = models.Album
        fields = (
            "id",
            "fid",
            "mbid",
            "title",
            "artist",
            "tracks",
            "release_date",
            "cover",
            "creation_date",
            "is_playable",
            "is_local",
            "tags",
            "attributed_to",
        )

    get_attributed_to = serialize_attributed_to

    def get_tracks(self, o):
        ordered_tracks = o.tracks.all()
        return AlbumTrackSerializer(ordered_tracks, many=True).data

    def get_is_playable(self, obj):
        try:
            return any(
                [bool(getattr(t, "playable_uploads", [])) for t in obj.tracks.all()]
            )
        except AttributeError:
            return None

    def get_tags(self, obj):
        tagged_items = getattr(obj, "_prefetched_tagged_items", [])
        return [ti.tag.name for ti in tagged_items]


class TrackAlbumSerializer(serializers.ModelSerializer):
    artist = ArtistSimpleSerializer(read_only=True)
    cover = cover_field

    class Meta:
        model = models.Album
        fields = (
            "id",
            "fid",
            "mbid",
            "title",
            "artist",
            "release_date",
            "cover",
            "creation_date",
            "is_local",
        )


class TrackUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Upload
        fields = (
            "uuid",
            "listen_url",
            "size",
            "duration",
            "bitrate",
            "mimetype",
            "extension",
        )


class TrackSerializer(serializers.ModelSerializer):
    artist = ArtistSimpleSerializer(read_only=True)
    album = TrackAlbumSerializer(read_only=True)
    uploads = serializers.SerializerMethodField()
    listen_url = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    attributed_to = serializers.SerializerMethodField()

    class Meta:
        model = models.Track
        fields = (
            "id",
            "fid",
            "mbid",
            "title",
            "album",
            "artist",
            "creation_date",
            "position",
            "disc_number",
            "uploads",
            "listen_url",
            "copyright",
            "license",
            "is_local",
            "tags",
            "attributed_to",
        )

    get_attributed_to = serialize_attributed_to

    def get_listen_url(self, obj):
        return obj.listen_url

    def get_uploads(self, obj):
        uploads = getattr(obj, "playable_uploads", [])
        return TrackUploadSerializer(uploads, many=True).data

    def get_tags(self, obj):
        tagged_items = getattr(obj, "_prefetched_tagged_items", [])
        return [ti.tag.name for ti in tagged_items]


@common_serializers.track_fields_for_update("name", "description", "privacy_level")
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

    def on_updated_fields(self, obj, before, after):
        routes.outbox.dispatch(
            {"type": "Update", "object": {"type": "Library"}}, context={"library": obj}
        )


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
            common_utils.on_commit(tasks.process_upload.delay, upload_id=pk)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "creation_date")


class SimpleAlbumSerializer(serializers.ModelSerializer):
    cover = cover_field

    class Meta:
        model = models.Album
        fields = ("id", "mbid", "title", "release_date", "cover")


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


def get_embed_url(type, id):
    return settings.FUNKWHALE_EMBED_URL + "?type={}&id={}".format(type, id)


class OembedSerializer(serializers.Serializer):
    format = serializers.ChoiceField(choices=["json"])
    url = serializers.URLField()
    maxheight = serializers.IntegerField(required=False)
    maxwidth = serializers.IntegerField(required=False)

    def validate(self, validated_data):
        try:
            match = common_utils.spa_resolve(
                urllib.parse.urlparse(validated_data["url"]).path
            )
        except urls.exceptions.Resolver404:
            raise serializers.ValidationError(
                "Invalid URL {}".format(validated_data["url"])
            )
        data = {
            "version": "1.0",
            "type": "rich",
            "provider_name": settings.APP_NAME,
            "provider_url": settings.FUNKWHALE_URL,
            "height": validated_data.get("maxheight") or 400,
            "width": validated_data.get("maxwidth") or 600,
        }
        embed_id = None
        embed_type = None
        if match.url_name == "library_track":
            qs = models.Track.objects.select_related("artist", "album__artist").filter(
                pk=int(match.kwargs["pk"])
            )
            try:
                track = qs.get()
            except models.Track.DoesNotExist:
                raise serializers.ValidationError(
                    "No track matching id {}".format(match.kwargs["pk"])
                )
            embed_type = "track"
            embed_id = track.pk
            data["title"] = "{} by {}".format(track.title, track.artist.name)
            if track.album.cover:
                data["thumbnail_url"] = federation_utils.full_url(
                    track.album.cover.crop["400x400"].url
                )
                data["thumbnail_width"] = 400
                data["thumbnail_height"] = 400
            data["description"] = track.full_name
            data["author_name"] = track.artist.name
            data["height"] = 150
            data["author_url"] = federation_utils.full_url(
                common_utils.spa_reverse(
                    "library_artist", kwargs={"pk": track.artist.pk}
                )
            )
        elif match.url_name == "library_album":
            qs = models.Album.objects.select_related("artist").filter(
                pk=int(match.kwargs["pk"])
            )
            try:
                album = qs.get()
            except models.Album.DoesNotExist:
                raise serializers.ValidationError(
                    "No album matching id {}".format(match.kwargs["pk"])
                )
            embed_type = "album"
            embed_id = album.pk
            if album.cover:
                data["thumbnail_url"] = federation_utils.full_url(
                    album.cover.crop["400x400"].url
                )
                data["thumbnail_width"] = 400
                data["thumbnail_height"] = 400
            data["title"] = "{} by {}".format(album.title, album.artist.name)
            data["description"] = "{} by {}".format(album.title, album.artist.name)
            data["author_name"] = album.artist.name
            data["height"] = 400
            data["author_url"] = federation_utils.full_url(
                common_utils.spa_reverse(
                    "library_artist", kwargs={"pk": album.artist.pk}
                )
            )
        elif match.url_name == "library_artist":
            qs = models.Artist.objects.filter(pk=int(match.kwargs["pk"]))
            try:
                artist = qs.get()
            except models.Artist.DoesNotExist:
                raise serializers.ValidationError(
                    "No artist matching id {}".format(match.kwargs["pk"])
                )
            embed_type = "artist"
            embed_id = artist.pk
            album = (
                artist.albums.filter(cover__isnull=False)
                .exclude(cover="")
                .order_by("-id")
                .first()
            )

            if album and album.cover:
                data["thumbnail_url"] = federation_utils.full_url(
                    album.cover.crop["400x400"].url
                )
                data["thumbnail_width"] = 400
                data["thumbnail_height"] = 400
            data["title"] = artist.name
            data["description"] = artist.name
            data["author_name"] = artist.name
            data["height"] = 400
            data["author_url"] = federation_utils.full_url(
                common_utils.spa_reverse("library_artist", kwargs={"pk": artist.pk})
            )
        else:
            raise serializers.ValidationError(
                "Unsupported url: {}".format(validated_data["url"])
            )
        data[
            "html"
        ] = '<iframe width="{}" height="{}" scrolling="no" frameborder="no" src="{}"></iframe>'.format(
            data["width"], data["height"], get_embed_url(embed_type, embed_id)
        )
        return data

    def create(self, data):
        return data
