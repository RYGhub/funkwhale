from django.conf import settings

from rest_framework import serializers

from funkwhale_api.activity import serializers as activity_serializers
from funkwhale_api.music.serializers import TrackSerializerNested
from funkwhale_api.music.serializers import TrackActivitySerializer
from funkwhale_api.users.serializers import UserActivitySerializer

from . import models


class TrackFavoriteActivitySerializer(activity_serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    object = TrackActivitySerializer(source='track')
    actor = UserActivitySerializer(source='user')
    published = serializers.DateTimeField(source='creation_date')

    class Meta:
        model = models.TrackFavorite
        fields = [
            'id',
            'local_id',
            'object',
            'type',
            'actor',
            'published'
        ]

    def get_actor(self, obj):
        return UserActivitySerializer(obj.user).data

    def get_type(self, obj):
        return 'Like'


class UserTrackFavoriteSerializer(serializers.ModelSerializer):
    # track = TrackSerializerNested(read_only=True)
    class Meta:
        model = models.TrackFavorite
        fields = ('id', 'track', 'creation_date')
