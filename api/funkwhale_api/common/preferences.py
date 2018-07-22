from django import forms
from django.conf import settings
from dynamic_preferences import serializers, types
from dynamic_preferences.registries import global_preferences_registry


class DefaultFromSettingMixin(object):
    def get_default(self):
        return getattr(settings, self.setting)


def get(pref):
    manager = global_preferences_registry.manager()
    return manager[pref]


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
