from django.forms import widgets
from dynamic_preferences import types
from dynamic_preferences.registries import global_preferences_registry

raven = types.Section("raven")
instance = types.Section("instance")


@global_preferences_registry.register
class InstanceName(types.StringPreference):
    show_in_api = True
    section = instance
    name = "name"
    default = ""
    verbose_name = "Public name"
    help_text = "The public name of your instance, displayed in the about page."
    field_kwargs = {"required": False}


@global_preferences_registry.register
class InstanceShortDescription(types.StringPreference):
    show_in_api = True
    section = instance
    name = "short_description"
    default = ""
    verbose_name = "Short description"
    help_text = "Instance succinct description, displayed in the about page."
    field_kwargs = {"required": False}


@global_preferences_registry.register
class InstanceLongDescription(types.StringPreference):
    show_in_api = True
    section = instance
    name = "long_description"
    verbose_name = "Long description"
    default = ""
    help_text = (
        "Instance long description, displayed in the about page (markdown allowed)."
    )
    widget = widgets.Textarea
    field_kwargs = {"required": False}


@global_preferences_registry.register
class RavenDSN(types.StringPreference):
    show_in_api = True
    section = raven
    name = "front_dsn"
    default = "https://9e0562d46b09442bb8f6844e50cbca2b@sentry.eliotberriot.com/4"
    verbose_name = "Raven DSN key (front-end)"

    help_text = (
        "A Raven DSN key used to report front-ent errors to "
        "a sentry instance. Keeping the default one will report errors to "
        "Funkwhale developers."
    )
    field_kwargs = {"required": False}


@global_preferences_registry.register
class InstanceNodeinfoEnabled(types.BooleanPreference):
    show_in_api = False
    section = instance
    name = "nodeinfo_enabled"
    default = True
    verbose_name = "Enable nodeinfo endpoint"
    help_text = (
        "This endpoint is needed for your about page to work. "
        "It's also helpful for the various monitoring "
        "tools that map and analyzize the fediverse, "
        "but you can disable it completely if needed."
    )


@global_preferences_registry.register
class InstanceNodeinfoPrivate(types.BooleanPreference):
    show_in_api = False
    section = instance
    name = "nodeinfo_private"
    default = False
    verbose_name = "Private mode in nodeinfo"
    help_text = (
        "Indicate in the nodeinfo endpoint that you do not want your instance "
        "to be tracked by third-party services. "
        "There is no guarantee these tools will honor this setting though."
    )


@global_preferences_registry.register
class InstanceNodeinfoStatsEnabled(types.BooleanPreference):
    show_in_api = False
    section = instance
    name = "nodeinfo_stats_enabled"
    default = True
    verbose_name = "Enable usage and library stats in nodeinfo endpoint"
    help_text = (
        "Disable this if you don't want to share usage and library statistics "
        "in the nodeinfo endpoint but don't want to disable it completely."
    )
