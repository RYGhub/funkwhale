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


@global_preferences_registry.register
class MaxChannels(types.IntegerPreference):
    show_in_api = True
    section = audio
    default = 20
    name = "max_channels"
    verbose_name = "Max channels allowed per user"
