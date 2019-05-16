import django_filters
from django import forms
from django.db import models

from . import search

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


def privacy_level_query(user, lookup_field="privacy_level", user_field="user"):
    if user.is_anonymous:
        return models.Q(**{lookup_field: "everyone"})

    return models.Q(
        **{"{}__in".format(lookup_field): ["instance", "everyone"]}
    ) | models.Q(**{lookup_field: "me", user_field: user})


class SearchFilter(django_filters.CharFilter):
    def __init__(self, *args, **kwargs):
        self.search_fields = kwargs.pop("search_fields")
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if not value:
            return qs
        query = search.get_query(value, self.search_fields)
        return qs.filter(query)


class SmartSearchFilter(django_filters.CharFilter):
    def __init__(self, *args, **kwargs):
        self.config = kwargs.pop("config")
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if not value:
            return qs
        try:
            cleaned = self.config.clean(value)
        except (forms.ValidationError):
            return qs.none()
        return search.apply(qs, cleaned)
