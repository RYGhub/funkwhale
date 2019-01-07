from rest_framework import serializers

from . import models


class ActorRelatedField(serializers.EmailField):
    def to_representation(self, value):
        return value.full_username

    def to_interal_value(self, value):
        value = super().to_interal_value(value)
        username, domain = value.split("@")
        try:
            return models.Actor.objects.get(
                preferred_username=username, domain_id=domain
            )
        except models.Actor.DoesNotExist:
            raise serializers.ValidationError("Invalid actor name")
