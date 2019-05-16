import django_filters

from rest_framework import serializers

from . import models
from . import utils


class ActorRelatedField(serializers.EmailField):
    def to_representation(self, value):
        return value.full_username

    def to_internal_value(self, value):
        value = super().to_internal_value(value)
        username, domain = value.split("@")
        try:
            return models.Actor.objects.get(
                preferred_username=username, domain_id=domain
            )
        except models.Actor.DoesNotExist:
            raise serializers.ValidationError("Invalid actor name")


class DomainFromURLFilter(django_filters.CharFilter):
    def __init__(self, *args, **kwargs):
        self.url_field = kwargs.pop("url_field", "fid")
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if not value:
            return qs
        query = utils.get_domain_query_from_url(value, self.url_field)
        return qs.filter(query)
