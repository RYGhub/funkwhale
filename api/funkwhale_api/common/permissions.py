from django.conf import settings

from rest_framework.permissions import BasePermission


class ConditionalAuthentication(BasePermission):

    def has_permission(self, request, view):
        if settings.API_AUTHENTICATION_REQUIRED:
            return request.user and request.user.is_authenticated
        return True
