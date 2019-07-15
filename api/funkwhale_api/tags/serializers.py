from rest_framework import serializers

from . import models


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ["name", "creation_date"]


class TagNameField(serializers.CharField):
    def to_internal_value(self, value):
        value = super().to_internal_value(value)
        if not models.TAG_REGEX.match(value):
            raise serializers.ValidationError('Invalid tag "{}"'.format(value))
        return value
