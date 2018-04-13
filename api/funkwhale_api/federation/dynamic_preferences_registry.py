from django.forms import widgets

from dynamic_preferences import types
from dynamic_preferences.registries import global_preferences_registry

federation = types.Section('federation')


@global_preferences_registry.register
class MusicCacheDuration(types.IntPreference):
    show_in_api = True
    section = federation
    name = 'music_cache_duration'
    default = 60 * 24 * 2
    verbose_name = 'Music cache duration'
    help_text = (
        'How much minutes do you want to keep a copy of federated tracks'
        'locally? Federated files that were not listened in this interval '
        'will be erased and refetched from the remote on the next listening.'
    )
