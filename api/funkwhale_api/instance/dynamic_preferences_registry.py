from dynamic_preferences import types
from dynamic_preferences.registries import global_preferences_registry

raven = types.Section('raven')


@global_preferences_registry.register
class RavenDSN(types.StringPreference):
    show_in_api = True
    section = raven
    name = 'front_dsn'
    default = 'https://9e0562d46b09442bb8f6844e50cbca2b@sentry.eliotberriot.com/4'
    verbose_name = (
        'A raven DSN key used to report front-ent errors to '
        'a sentry instance'
    )
    help_text = (
        'Keeping the default one will report errors to funkwhale developers'
    )


SENTRY_HELP_TEXT = (
    'Error reporting is disabled by default but you can enable it if'
    ' you want to help us improve funkwhale'
)


@global_preferences_registry.register
class RavenEnabled(types.BooleanPreference):
    show_in_api = True
    section = raven
    name = 'front_enabled'
    default = False
    verbose_name = (
        'Wether error reporting to a Sentry instance using raven is enabled'
        ' for front-end errors'
    )
