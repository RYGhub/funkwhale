from dynamic_preferences import types
from dynamic_preferences.registries import global_preferences_registry

from funkwhale_api.common import preferences

playlists = types.Section("playlists")


@global_preferences_registry.register
class MaxTracks(preferences.DefaultFromSettingMixin, types.IntegerPreference):
    show_in_api = True
    section = playlists
    name = "max_tracks"
    verbose_name = "Max tracks per playlist"
    setting = "PLAYLISTS_MAX_TRACKS"
    field_kwargs = {"required": False}
