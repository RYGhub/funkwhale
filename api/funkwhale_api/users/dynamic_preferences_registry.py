from dynamic_preferences import types
from dynamic_preferences.registries import global_preferences_registry

users = types.Section('users')


@global_preferences_registry.register
class RegistrationEnabled(types.BooleanPreference):
    show_in_api = True
    section = users
    name = 'registration_enabled'
    default = False
    verbose_name = (
        'Can visitors open a new account on this instance?'
    )
