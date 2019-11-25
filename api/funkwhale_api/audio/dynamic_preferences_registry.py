from dynamic_preferences import types
from dynamic_preferences.registries import global_preferences_registry

audio = types.Section("audio")


@global_preferences_registry.register
class ChannelsEnabled(types.BooleanPreference):
    section = audio
    name = "channels_enabled"
    default = True
    verbose_name = "Enable channels"
    help_text = (
        "If disabled, the channels feature will be completely switched off, "
        "and users won't be able to create channels or subscribe to them."
    )
