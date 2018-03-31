import cryptography

from django.contrib.auth.models import AnonymousUser

from rest_framework import authentication
from rest_framework import exceptions

from . import actors
from . import keys
from . import serializers
from . import signing
from . import utils


class SignatureAuthentication(authentication.BaseAuthentication):
    def authenticate_actor(self, request):
        headers = utils.clean_wsgi_headers(request.META)
        try:
            signature = headers['Signature']
            key_id = keys.get_key_id_from_signature_header(signature)
        except KeyError:
            return
        except ValueError as e:
            raise exceptions.AuthenticationFailed(str(e))

        try:
            actor_data = actors.get_actor_data(key_id)
        except Exception as e:
            raise exceptions.AuthenticationFailed(str(e))

        try:
            public_key = actor_data['publicKey']['publicKeyPem']
        except KeyError:
            raise exceptions.AuthenticationFailed('No public key found')

        serializer = serializers.ActorSerializer(data=actor_data)
        if not serializer.is_valid():
            raise exceptions.AuthenticationFailed('Invalid actor payload: {}'.format(serializer.errors))

        try:
            signing.verify_django(request, public_key.encode('utf-8'))
        except cryptography.exceptions.InvalidSignature:
            raise exceptions.AuthenticationFailed('Invalid signature')

        return serializer.build()

    def authenticate(self, request):
        actor = self.authenticate_actor(request)
        user = AnonymousUser()
        setattr(request, 'actor', actor)
        return (user, None)
