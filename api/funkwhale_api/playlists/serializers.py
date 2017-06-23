from rest_framework import serializers
from taggit.models import Tag

from funkwhale_api.music.serializers import TrackSerializerNested

from . import models


class PlaylistTrackSerializer(serializers.ModelSerializer):
    track = TrackSerializerNested()

    class Meta:
        model = models.PlaylistTrack
        fields = ('id', 'track', 'playlist', 'position')


class PlaylistTrackCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.PlaylistTrack
        fields = ('id', 'track', 'playlist', 'position')


class PlaylistSerializer(serializers.ModelSerializer):
    playlist_tracks = PlaylistTrackSerializer(many=True, read_only=True)

    class Meta:
        model = models.Playlist
        fields = ('id', 'name', 'is_public', 'creation_date', 'playlist_tracks')
        read_only_fields = ['id', 'playlist_tracks', 'creation_date']
