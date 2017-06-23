from allauth.account.adapter import DefaultAccountAdapter

from django.conf import settings


class FunkwhaleAccountAdapter(DefaultAccountAdapter):

    def is_open_for_signup(self, request):

        if settings.REGISTRATION_MODE == "disabled":
            return False
        if settings.REGISTRATION_MODE == "public":
            return True

        return False
