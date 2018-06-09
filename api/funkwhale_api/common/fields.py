import django_filters

from django.db import models

from funkwhale_api.music import utils


PRIVACY_LEVEL_CHOICES = [
    ("me", "Only me"),
    ("followers", "Me and my followers"),
    ("instance", "Everyone on my instance, and my followers"),
    ("everyone", "Everyone, including people on other instances"),
]


def get_privacy_field():
    return models.CharField(
        max_length=30, choices=PRIVACY_LEVEL_CHOICES, default="instance"
    )


def privacy_level_query(user, lookup_field="privacy_level"):
    if user.is_anonymous:
        return models.Q(**{lookup_field: "everyone"})

    return models.Q(
        **{"{}__in".format(lookup_field): ["followers", "instance", "everyone"]}
    )


class SearchFilter(django_filters.CharFilter):
    def __init__(self, *args, **kwargs):
        self.search_fields = kwargs.pop("search_fields")
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if not value:
            return qs
        query = utils.get_query(value, self.search_fields)
        return qs.filter(query)
