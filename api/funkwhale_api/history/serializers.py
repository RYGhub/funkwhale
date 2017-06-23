from rest_framework import serializers

from funkwhale_api.music.serializers import TrackSerializerNested
from . import models


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
