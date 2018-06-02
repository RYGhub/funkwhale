from django.conf import settings

from rest_framework.permissions import BasePermission

from funkwhale_api.common import preferences
from funkwhale_api.federation import actors
from funkwhale_api.federation import models


class Listen(BasePermission):

    def has_permission(self, request, view):
        if not preferences.get('common__api_authentication_required'):
            return True

        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            return True

        actor = getattr(request, 'actor', None)
        if actor is None:
            return False

        library = actors.SYSTEM_ACTORS['library'].get_actor_instance()
        return models.Follow.objects.filter(
            target=library,
            actor=actor,
            approved=True
        ).exists()
