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

    class Meta:
        model = models.Playlist
        fields = ('id', 'name', 'privacy_level', 'creation_date')
        read_only_fields = ['id', 'creation_date']
