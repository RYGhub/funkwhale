from django.conf import settings

from allauth.account.adapter import DefaultAccountAdapter
from dynamic_preferences.registries import global_preferences_registry


class FunkwhaleAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        manager = global_preferences_registry.manager()
        return manager["users__registration_enabled"]

    def send_mail(self, template_prefix, email, context):
        context["funkwhale_url"] = settings.FUNKWHALE_URL
        return super().send_mail(template_prefix, email, context)
