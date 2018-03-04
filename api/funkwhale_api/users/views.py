from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.decorators import list_route

from rest_auth.registration.views import RegisterView as BaseRegisterView
from allauth.account.adapter import get_adapter

from . import models
from . import serializers


class RegisterView(BaseRegisterView):

    def create(self, request, *args, **kwargs):
        if not self.is_open_for_signup(request):
            r = {
                'detail': 'Registration has been disabled',
            }
            return Response(r, status=403)
        return super().create(request, *args, **kwargs)

    def is_open_for_signup(self, request):
        return get_adapter().is_open_for_signup(request)


class UserViewSet(
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserWriteSerializer
    lookup_field = 'username'

    @list_route(methods=['get'])
    def me(self, request, *args, **kwargs):
        """Return information about the current user"""
        serializer = serializers.UserReadSerializer(request.user)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        if not self.request.user.username == kwargs.get('username'):
            return Response(status=403)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if not self.request.user.username == kwargs.get('username'):
            return Response(status=403)
        return super().partial_update(request, *args, **kwargs)
