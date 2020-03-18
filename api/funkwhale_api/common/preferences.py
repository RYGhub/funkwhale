import json

from django import forms
from django.contrib.postgres.forms import JSONField
from django.conf import settings
from dynamic_preferences import serializers, types
from dynamic_preferences.registries import global_preferences_registry


class DefaultFromSettingMixin(object):
    def get_default(self):
        return getattr(settings, self.setting)


def get(pref):
    manager = global_preferences_registry.manager()
    return manager[pref]


def all():
    manager = global_preferences_registry.manager()
    return manager.all()


def set(pref, value):
    manager = global_preferences_registry.manager()
    manager[pref] = value


class StringListSerializer(serializers.BaseSerializer):
    separator = ","
    sort = True

    @classmethod
    def to_db(cls, value, **kwargs):
        if not value:
            return

        if type(value) not in [list, tuple]:
            raise cls.exception(
                "Cannot serialize, value {} is not a list or a tuple".format(value)
            )

        if cls.sort:
            value = sorted(value)
        return cls.separator.join(value)

    @classmethod
    def to_python(cls, value, **kwargs):
        if not value:
            return []
        return value.split(",")


class StringListPreference(types.BasePreferenceType):
    serializer = StringListSerializer
    field_class = forms.MultipleChoiceField

    def get_api_additional_data(self):
        d = super(StringListPreference, self).get_api_additional_data()
        d["choices"] = self.get("choices")
        return d


class JSONSerializer(serializers.BaseSerializer):
    required = True

    @classmethod
    def to_db(cls, value, **kwargs):
        if not cls.required and value is None:
            return json.dumps(value)
        data_serializer = cls.data_serializer_class(data=value)
        if not data_serializer.is_valid():
            raise cls.exception(
                "{} is not a valid value: {}".format(value, data_serializer.errors)
            )
        value = data_serializer.validated_data
        try:
            return json.dumps(value, sort_keys=True)
        except TypeError:
            raise cls.exception(
                "Cannot serialize, value {} is not JSON serializable".format(value)
            )

    @classmethod
    def to_python(cls, value, **kwargs):
        return json.loads(value)


class SerializedPreference(types.BasePreferenceType):
    """
    A preference that store arbitrary JSON and validate it using a rest_framework
    serializer
    """

    serializer = JSONSerializer
    data_serializer_class = None
    field_class = JSONField
    widget = forms.Textarea

    @property
    def serializer(self):
        class _internal(JSONSerializer):
            data_serializer_class = self.data_serializer_class
            required = self.get("required")

        return _internal
