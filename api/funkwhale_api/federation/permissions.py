
from rest_framework.permissions import BasePermission

from funkwhale_api.common import preferences

from . import actors


class LibraryFollower(BasePermission):
    def has_permission(self, request, view):
        if not preferences.get("federation__music_needs_approval"):
            return True

        actor = getattr(request, "actor", None)
        if actor is None:
            return False

        library = actors.SYSTEM_ACTORS["library"].get_actor_instance()
        return library.received_follows.filter(approved=True, actor=actor).exists()
