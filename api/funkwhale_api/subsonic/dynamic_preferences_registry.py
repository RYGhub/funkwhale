from dynamic_preferences import types
from dynamic_preferences.registries import global_preferences_registry

subsonic = types.Section("subsonic")


@global_preferences_registry.register
class APIAutenticationRequired(types.BooleanPreference):
    section = subsonic
    show_in_api = True
    name = "enabled"
    default = True
    verbose_name = "Enabled Subsonic API"
    help_text = (
        "Funkwhale supports a subset of the Subsonic API, that makes "
        "it compatible with existing clients such as DSub for Android "
        "or Clementine for desktop. However, Subsonic protocol is less "
        "than ideal in terms of security and you can disable this feature "
        "completely using this flag."
    )
