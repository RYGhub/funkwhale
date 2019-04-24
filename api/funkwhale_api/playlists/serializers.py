from django.db import transaction
from rest_framework import serializers

from funkwhale_api.common import preferences
from funkwhale_api.music.models import Track
from funkwhale_api.music.serializers import TrackSerializer
from funkwhale_api.users.serializers import UserBasicSerializer

from . import models


class PlaylistTrackSerializer(serializers.ModelSerializer):
    # track = TrackSerializer()
    track = serializers.SerializerMethodField()

    class Meta:
        model = models.PlaylistTrack
        fields = ("id", "track", "playlist", "index", "creation_date")

    def get_track(self, o):
        track = o._prefetched_track if hasattr(o, "_prefetched_track") else o.track
        return TrackSerializer(track).data


class PlaylistTrackWriteSerializer(serializers.ModelSerializer):
    index = serializers.IntegerField(required=False, min_value=0, allow_null=True)
    allow_duplicates = serializers.BooleanField(required=False)

    class Meta:
        model = models.PlaylistTrack
        fields = ("id", "track", "playlist", "index", "allow_duplicates")

    def validate_playlist(self, value):
        if self.context.get("request"):
            # validate proper ownership on the playlist
            if self.context["request"].user != value.user:
                raise serializers.ValidationError(
                    "You do not have the permission to edit this playlist"
                )
        existing = value.playlist_tracks.count()
        max_tracks = preferences.get("playlists__max_tracks")
        if existing >= max_tracks:
            raise serializers.ValidationError(
                "Playlist has reached the maximum of {} tracks".format(max_tracks)
            )
        return value

    @transaction.atomic
    def create(self, validated_data):
        index = validated_data.pop("index", None)
        allow_duplicates = validated_data.pop("allow_duplicates", True)
        instance = super().create(validated_data)

        instance.playlist.insert(instance, index, allow_duplicates)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        update_index = "index" in validated_data
        index = validated_data.pop("index", None)
        allow_duplicates = validated_data.pop("allow_duplicates", True)
        super().update(instance, validated_data)
        if update_index:
            instance.playlist.insert(instance, index, allow_duplicates)

        return instance

    def get_unique_together_validators(self):
        """
        We explicitely disable unique together validation here
        because it collides with our internal logic
        """
        return []


class PlaylistSerializer(serializers.ModelSerializer):
    tracks_count = serializers.SerializerMethodField(read_only=True)
    duration = serializers.SerializerMethodField(read_only=True)
    album_covers = serializers.SerializerMethodField(read_only=True)
    user = UserBasicSerializer(read_only=True)
    is_playable = serializers.SerializerMethodField()

    class Meta:
        model = models.Playlist
        fields = (
            "id",
            "name",
            "user",
            "modification_date",
            "creation_date",
            "privacy_level",
            "tracks_count",
            "album_covers",
            "duration",
            "is_playable",
        )
        read_only_fields = ["id", "modification_date", "creation_date"]

    def get_is_playable(self, obj):
        try:
            return bool(obj.playable_plts)
        except AttributeError:
            return None

    def get_tracks_count(self, obj):
        try:
            return obj.tracks_count
        except AttributeError:
            # no annotation?
            return obj.playlist_tracks.count()

    def get_duration(self, obj):
        try:
            return obj.duration
        except AttributeError:
            # no annotation?
            return 0

    def get_album_covers(self, obj):
        try:
            plts = obj.plts_for_cover
        except AttributeError:
            return []

        excluded_artists = []
        try:
            user = self.context["request"].user
        except (KeyError, AttributeError):
            user = None
        if user and user.is_authenticated:
            excluded_artists = list(
                user.content_filters.values_list("target_artist", flat=True)
            )

        covers = []
        max_covers = 5
        for plt in plts:
            if plt.track.album.artist_id in excluded_artists:
                continue
            url = plt.track.album.cover.crop["200x200"].url
            if url in covers:
                continue
            covers.append(url)
            if len(covers) >= max_covers:
                break

        full_urls = []
        for url in covers:
            if "request" in self.context:
                url = self.context["request"].build_absolute_uri(url)
            full_urls.append(url)
        return full_urls


class PlaylistAddManySerializer(serializers.Serializer):
    tracks = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Track.objects.for_nested_serialization()
    )
    allow_duplicates = serializers.BooleanField(required=False)

    class Meta:
        fields = "allow_duplicates"
