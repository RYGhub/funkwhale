from django.forms import widgets

from dynamic_preferences import types
from dynamic_preferences.registries import global_preferences_registry

federation = types.Section('federation')


@global_preferences_registry.register
class FederationPrivateKey(types.StringPreference):
    show_in_api = False
    section = federation
    name = 'private_key'
    default = ''
    help_text = (
        'Instance private key, used for signing federation HTTP requests'
    )
    verbose_name = (
        'Instance private key (keep it secret, do not change it)'
    )


@global_preferences_registry.register
class FederationPublicKey(types.StringPreference):
    show_in_api = False
    section = federation
    name = 'public_key'
    default = ''
    help_text = (
        'Instance public key, used for signing federation HTTP requests'
    )
    verbose_name = (
        'Instance public key (do not change it)'
    )
