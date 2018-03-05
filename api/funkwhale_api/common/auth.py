from urllib.parse import parse_qs

import jwt

from django.contrib.auth.models import AnonymousUser
from django.utils.encoding import smart_text

from rest_framework import exceptions
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.authentication import BaseJSONWebTokenAuthentication

from funkwhale_api.users.models import User


class TokenHeaderAuth(BaseJSONWebTokenAuthentication):
    def get_jwt_value(self, request):

        try:
            qs = request.get('query_string', b'').decode('utf-8')
            parsed = parse_qs(qs)
            token = parsed['token'][0]
        except KeyError:
            raise exceptions.AuthenticationFailed('No token')

        if not token:
            raise exceptions.AuthenticationFailed('Empty token')

        return token


class TokenAuthMiddleware:
    """
    Custom middleware (insecure) that takes user IDs from the query string.
    """

    def __init__(self, inner):
        # Store the ASGI application we were passed
        self.inner = inner

    def __call__(self, scope):
        auth = TokenHeaderAuth()
        try:
            user, token = auth.authenticate(scope)
        except (User.DoesNotExist, exceptions.AuthenticationFailed):
            user = AnonymousUser()

        scope['user'] = user
        return self.inner(scope)
