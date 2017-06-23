from rest_framework import serializers

from funkwhale_api.music.serializers import TrackSerializerNested
from . import models


class RadioSessionTrackSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = models.RadioSessionTrack
        fields = ('session',)


class RadioSessionTrackSerializer(serializers.ModelSerializer):
    track = TrackSerializerNested()

    class Meta:
        model = models.RadioSessionTrack
        fields = ('id', 'session', 'position', 'track')


class RadioSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RadioSession
        fields = ('id', 'radio_type', 'related_object_id', 'user', 'creation_date', 'session_key')

    def create(self, validated_data):
        if self.context.get('user'):
            validated_data['user'] = self.context.get('user')
        else:
            validated_data['session_key'] = self.context['session_key']
        if validated_data.get('related_object_id'):
            from . import radios
            radio = radios.registry[validated_data['radio_type']]()
            validated_data['related_object'] = radio.get_related_object(validated_data['related_object_id'])
        return super().create(validated_data)
