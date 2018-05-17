from dynamic_preferences import types
from dynamic_preferences.registries import global_preferences_registry

users = types.Section('users')


@global_preferences_registry.register
class RegistrationEnabled(types.BooleanPreference):
    show_in_api = True
    section = users
    name = 'registration_enabled'
    default = False
    verbose_name = 'Open registrations to new users'
    help_text = (
        'When enabled, new users will be able to register on this instance.'
    )
