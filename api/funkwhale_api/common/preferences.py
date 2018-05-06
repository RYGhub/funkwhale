from django.conf import settings
from dynamic_preferences.registries import global_preferences_registry


class DefaultFromSettingMixin(object):
    def get_default(self):
        return getattr(settings, self.setting)


def get(pref):
    manager = global_preferences_registry.manager()
    return manager[pref]
