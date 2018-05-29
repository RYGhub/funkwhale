from django.db import transaction
from rest_framework import serializers

from funkwhale_api.common import serializers as common_serializers
from funkwhale_api.music import models as music_models

from . import filters


class ManageTrackFileArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = music_models.Artist
        fields = [
            'id',
            'mbid',
            'creation_date',
            'name',
        ]


class ManageTrackFileAlbumSerializer(serializers.ModelSerializer):
    artist = ManageTrackFileArtistSerializer()

    class Meta:
        model = music_models.Album
        fields = (
            'id',
            'mbid',
            'title',
            'artist',
            'release_date',
            'cover',
            'creation_date',
        )


class ManageTrackFileTrackSerializer(serializers.ModelSerializer):
    artist = ManageTrackFileArtistSerializer()
    album = ManageTrackFileAlbumSerializer()

    class Meta:
        model = music_models.Track
        fields = (
            'id',
            'mbid',
            'title',
            'album',
            'artist',
            'creation_date',
            'position',
        )


class ManageTrackFileSerializer(serializers.ModelSerializer):
    track = ManageTrackFileTrackSerializer()

    class Meta:
        model = music_models.TrackFile
        fields = (
            'id',
            'path',
            'source',
            'filename',
            'mimetype',
            'track',
            'duration',
            'mimetype',
            'bitrate',
            'size',
            'path',
            'library_track',
        )


class ManageTrackFileActionSerializer(common_serializers.ActionSerializer):
    actions = ['delete']
    dangerous_actions = ['delete']
    filterset_class = filters.ManageTrackFileFilterSet

    @transaction.atomic
    def handle_delete(self, objects):
        return objects.delete()
