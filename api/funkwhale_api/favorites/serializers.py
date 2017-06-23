from rest_framework import serializers

from funkwhale_api.music.serializers import TrackSerializerNested

from . import models


class UserTrackFavoriteSerializer(serializers.ModelSerializer):
    # track = TrackSerializerNested(read_only=True)
    class Meta:
        model = models.TrackFavorite
        fields = ('id', 'track', 'creation_date')
