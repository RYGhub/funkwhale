import operator

from django.conf import settings
from django.http import Http404

from rest_framework.permissions import BasePermission, DjangoModelPermissions


class ConditionalAuthentication(BasePermission):

    def has_permission(self, request, view):
        if settings.API_AUTHENTICATION_REQUIRED:
            return request.user and request.user.is_authenticated
        return True


class HasModelPermission(DjangoModelPermissions):
    """
    Same as DjangoModelPermissions, but we pin the model:

        class MyModelPermission(HasModelPermission):
            model = User
    """
    def get_required_permissions(self, method, model_cls):
        return super().get_required_permissions(method, self.model)


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
        'GET': 'read',
        'OPTIONS': 'read',
        'HEAD': 'read',
        'POST': 'write',
        'PUT': 'write',
        'PATCH': 'write',
        'DELETE': 'write',
    }

    def has_object_permission(self, request, view, obj):
        method_check = self.perms_map[request.method]
        owner_checks = getattr(view, 'owner_checks', ['read', 'write'])
        if method_check not in owner_checks:
            # check not enabled
            return True

        owner_field = getattr(view, 'owner_field', 'user')
        owner = operator.attrgetter(owner_field)(obj)
        if owner != request.user:
            raise Http404
        return True
