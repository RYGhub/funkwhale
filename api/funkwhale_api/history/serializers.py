from rest_framework import serializers

from funkwhale_api.activity import serializers as activity_serializers
from funkwhale_api.music.serializers import TrackSerializerNested
from funkwhale_api.music.serializers import TrackActivitySerializer
from funkwhale_api.users.serializers import UserActivitySerializer

from . import models


class ListeningActivitySerializer(activity_serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    object = TrackActivitySerializer(source='track')
    actor = UserActivitySerializer(source='user')
    published = serializers.DateTimeField(source='end_date')

    class Meta:
        model = models.Listening
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
        return 'Listen'


class ListeningSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Listening
        fields = ('id', 'user', 'session_key', 'track', 'end_date')


    def create(self, validated_data):
        if self.context.get('user'):
            validated_data['user'] = self.context.get('user')
        else:
            validated_data['session_key'] = self.context['session_key']

        return super().create(validated_data)
