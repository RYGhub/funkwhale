from allauth.account.adapter import get_adapter
from rest_auth.registration.views import RegisterView as BaseRegisterView
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from funkwhale_api.common import preferences

from . import models, serializers


class RegisterView(BaseRegisterView):
    serializer_class = serializers.RegisterSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        invitation_code = request.data.get("invitation")
        if not invitation_code and not self.is_open_for_signup(request):
            r = {"detail": "Registration has been disabled"}
            return Response(r, status=403)
        return super().create(request, *args, **kwargs)

    def is_open_for_signup(self, request):
        return get_adapter().is_open_for_signup(request)


class UserViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserWriteSerializer
    lookup_field = "username"
    lookup_value_regex = r"[a-zA-Z0-9-_.]+"
    required_scope = "profile"

    @action(methods=["get"], detail=False)
    def me(self, request, *args, **kwargs):
        """Return information about the current user"""
        serializer = serializers.MeSerializer(request.user)
        return Response(serializer.data)

    @action(
        methods=["get", "post", "delete"],
        required_scope="security",
        url_path="subsonic-token",
        detail=True,
    )
    def subsonic_token(self, request, *args, **kwargs):
        if not self.request.user.username == kwargs.get("username"):
            return Response(status=403)
        if not preferences.get("subsonic__enabled"):
            return Response(status=405)
        if request.method.lower() == "get":
            return Response(
                {"subsonic_api_token": self.request.user.subsonic_api_token}
            )
        if request.method.lower() == "delete":
            self.request.user.subsonic_api_token = None
            self.request.user.save(update_fields=["subsonic_api_token"])
            return Response(status=204)
        self.request.user.update_subsonic_api_token()
        self.request.user.save(update_fields=["subsonic_api_token"])
        data = {"subsonic_api_token": self.request.user.subsonic_api_token}
        return Response(data)

    def update(self, request, *args, **kwargs):
        if not self.request.user.username == kwargs.get("username"):
            return Response(status=403)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if not self.request.user.username == kwargs.get("username"):
            return Response(status=403)
        return super().partial_update(request, *args, **kwargs)
