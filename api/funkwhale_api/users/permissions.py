from rest_framework.permissions import BasePermission


class HasUserPermission(BasePermission):
    """
    Ensure the request user has the proper permissions.

    Usage:

    class MyView(APIView):
        permission_classes = [HasUserPermission]
        required_permissions = ['federation']
    """
    def has_permission(self, request, view):
        if not hasattr(request, 'user') or not request.user:
            return False
        if request.user.is_anonymous:
            return False
        operator = getattr(view, 'permission_operator', 'and')
        return request.user.has_permissions(
            *view.required_permissions, operator=operator)
