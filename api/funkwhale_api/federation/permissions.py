from django.conf import settings

from rest_framework.permissions import BasePermission

from . import actors


class LibraryFollower(BasePermission):

    def has_permission(self, request, view):
        if not settings.FEDERATION_MUSIC_NEEDS_APPROVAL:
            return True

        actor = getattr(request, 'actor', None)
        if actor is None:
            return False

        library = actors.SYSTEM_ACTORS['library'].get_actor_instance()
        return library.received_follows.filter(
            approved=True, actor=actor).exists()
