from allauth.account.adapter import DefaultAccountAdapter

from dynamic_preferences.registries import global_preferences_registry


class FunkwhaleAccountAdapter(DefaultAccountAdapter):

    def is_open_for_signup(self, request):
        manager = global_preferences_registry.manager()
        return manager['users__registration_enabled']
