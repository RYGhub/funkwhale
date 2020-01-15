from rest_framework import exceptions, mixins, viewsets

from django import http

from funkwhale_api.common import permissions
from funkwhale_api.common import preferences
from funkwhale_api.users.oauth import permissions as oauth_permissions

from . import filters, models, serializers


class ChannelsMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not preferences.get("audio__channels_enabled"):
            return http.HttpResponse(status=405)
        return super().dispatch(request, *args, **kwargs)


class ChannelViewSet(
    ChannelsMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = "uuid"
    filterset_class = filters.ChannelFilter
    serializer_class = serializers.ChannelSerializer
    queryset = (
        models.Channel.objects.all()
        .prefetch_related("library", "attributed_to", "artist__description", "actor")
        .order_by("-creation_date")
    )
    permission_classes = [
        oauth_permissions.ScopePermission,
        permissions.OwnerPermission,
    ]
    required_scope = "libraries"
    anonymous_policy = "setting"
    owner_checks = ["write"]
    owner_field = "attributed_to.user"
    owner_exception = exceptions.PermissionDenied

    def get_serializer_class(self):
        if self.request.method.lower() in ["head", "get", "options"]:
            return serializers.ChannelSerializer
        elif self.action in ["update", "partial_update"]:
            return serializers.ChannelUpdateSerializer
        return serializers.ChannelCreateSerializer

    def perform_create(self, serializer):
        return serializer.save(attributed_to=self.request.user.actor)
