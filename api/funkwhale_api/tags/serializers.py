from rest_framework import serializers

from django.conf import settings

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


class TagsListField(serializers.ListField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("min_length", 0)
        kwargs.setdefault("child", TagNameField())
        super().__init__(*args, **kwargs)

    def to_internal_value(self, value):
        value = super().to_internal_value(value)
        if not value:
            return value
        # we ignore any extra tags if the length of the list is higher
        # than our accepted size
        return value[: settings.TAGS_MAX_BY_OBJ]
