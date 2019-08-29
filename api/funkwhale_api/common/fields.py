import django_filters
from django import forms
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from rest_framework import serializers

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


class GenericRelation(serializers.JSONField):
    def __init__(self, choices, *args, **kwargs):
        self.choices = choices
        self.encoder = kwargs.setdefault("encoder", DjangoJSONEncoder)
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        if not value:
            return
        type = None
        id = None
        id_attr = None
        for key, choice in self.choices.items():
            if isinstance(value, choice["queryset"].model):
                type = key
                id_attr = choice.get("id_attr", "id")
                id = getattr(value, id_attr)
                break

        if type:
            return {"type": type, id_attr: id}

    def to_internal_value(self, v):
        v = super().to_internal_value(v)

        if not v or not isinstance(v, dict):
            raise serializers.ValidationError("Invalid data")

        try:
            type = v["type"]
            field = serializers.ChoiceField(choices=list(self.choices.keys()))
            type = field.to_internal_value(type)
        except (TypeError, KeyError, serializers.ValidationError):
            raise serializers.ValidationError("Invalid type")

        conf = self.choices[type]
        id_attr = conf.get("id_attr", "id")
        id_field = conf.get("id_field", serializers.IntegerField(min_value=1))
        queryset = conf["queryset"]
        try:
            id_value = v[id_attr]
            id_value = id_field.to_internal_value(id_value)
        except (TypeError, KeyError, serializers.ValidationError):
            raise serializers.ValidationError("Invalid {}".format(id_attr))

        query_getter = conf.get(
            "get_query", lambda attr, value: models.Q(**{attr: value})
        )
        query = query_getter(id_attr, id_value)
        try:
            obj = queryset.get(query)
        except queryset.model.DoesNotExist:
            raise serializers.ValidationError("Object not found")

        return obj
