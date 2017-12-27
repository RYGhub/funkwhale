from django.conf import settings

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
