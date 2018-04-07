from django.conf import settings

from rest_framework.permissions import BasePermission

from funkwhale_api.federation import actors


class Listen(BasePermission):

    def has_permission(self, request, view):
        if not settings.PROTECT_AUDIO_FILES:
            return True

        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            return True

        actor = getattr(request, 'actor', None)
        if actor is None:
            return False

        library = actors.SYSTEM_ACTORS['library'].get_actor_instance()
        return library.followers.filter(url=actor.url).exists()
