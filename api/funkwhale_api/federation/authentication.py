import cryptography
import logging

from django.contrib.auth.models import AnonymousUser
from rest_framework import authentication, exceptions

from funkwhale_api.moderation import models as moderation_models
from . import actors, exceptions, keys, signing, utils


logger = logging.getLogger(__name__)


class SignatureAuthentication(authentication.BaseAuthentication):
    def authenticate_actor(self, request):
        headers = utils.clean_wsgi_headers(request.META)
        try:
            signature = headers["Signature"]
            key_id = keys.get_key_id_from_signature_header(signature)
        except KeyError:
            return
        except ValueError as e:
            raise exceptions.AuthenticationFailed(str(e))

        try:
            actor_url = key_id.split("#")[0]
        except (TypeError, IndexError, AttributeError):
            raise exceptions.AuthenticationFailed("Invalid key id")

        policies = (
            moderation_models.InstancePolicy.objects.active()
            .filter(block_all=True)
            .matching_url(actor_url)
        )
        if policies.exists():
            raise exceptions.BlockedActorOrDomain()

        try:
            actor = actors.get_actor(actor_url)
        except Exception as e:
            logger.info(
                "Discarding HTTP request from blocked actor/domain %s", actor_url
            )
            raise exceptions.AuthenticationFailed(str(e))

        if not actor.public_key:
            raise exceptions.AuthenticationFailed("No public key found")

        try:
            signing.verify_django(request, actor.public_key.encode("utf-8"))
        except cryptography.exceptions.InvalidSignature:
            raise exceptions.AuthenticationFailed("Invalid signature")

        return actor

    def authenticate(self, request):
        setattr(request, "actor", None)
        actor = self.authenticate_actor(request)
        if not actor:
            return
        user = AnonymousUser()
        setattr(request, "actor", actor)
        return (user, None)
