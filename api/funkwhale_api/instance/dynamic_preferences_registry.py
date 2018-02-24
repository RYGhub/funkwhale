from django.forms import widgets

from dynamic_preferences import types
from dynamic_preferences.registries import global_preferences_registry

raven = types.Section('raven')
instance = types.Section('instance')


@global_preferences_registry.register
class InstanceName(types.StringPreference):
    show_in_api = True
    section = instance
    name = 'name'
    default = ''
    help_text = 'Instance public name'
    verbose_name = 'The public name of your instance'


@global_preferences_registry.register
class InstanceShortDescription(types.StringPreference):
    show_in_api = True
    section = instance
    name = 'short_description'
    default = ''
    verbose_name = 'Instance succinct description'


@global_preferences_registry.register
class InstanceLongDescription(types.StringPreference):
    show_in_api = True
    section = instance
    name = 'long_description'
    default = ''
    help_text = 'Instance long description (markdown allowed)'
    field_kwargs = {
        'widget': widgets.Textarea
    }

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
