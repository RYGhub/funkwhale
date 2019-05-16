import operator

from django.http import Http404
from rest_framework.permissions import BasePermission

from funkwhale_api.common import preferences


class ConditionalAuthentication(BasePermission):
    def has_permission(self, request, view):
        if preferences.get("common__api_authentication_required"):
            return (request.user and request.user.is_authenticated) or (
                hasattr(request, "actor") and request.actor
            )
        return True


class OwnerPermission(BasePermission):
    """
    Ensure the request user is the owner of the object.

    Usage:

    class MyView(APIView):
        model = MyModel
        permission_classes = [OwnerPermission]
        owner_field = 'owner'
        owner_checks = ['read', 'write']
    """

    perms_map = {
        "GET": "read",
        "OPTIONS": "read",
        "HEAD": "read",
        "POST": "write",
        "PUT": "write",
        "PATCH": "write",
        "DELETE": "write",
    }

    def has_object_permission(self, request, view, obj):
        method_check = self.perms_map[request.method]
        owner_checks = getattr(view, "owner_checks", ["read", "write"])
        if method_check not in owner_checks:
            # check not enabled
            return True

        owner_field = getattr(view, "owner_field", "user")
        owner = operator.attrgetter(owner_field)(obj)
        if not owner or not request.user.is_authenticated or owner != request.user:
            raise Http404
        return True
