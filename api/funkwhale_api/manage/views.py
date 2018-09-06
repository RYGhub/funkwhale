from rest_framework import mixins, response, viewsets
from rest_framework.decorators import list_route

from funkwhale_api.common import preferences
from funkwhale_api.music import models as music_models
from funkwhale_api.requests import models as requests_models
from funkwhale_api.users import models as users_models
from funkwhale_api.users.permissions import HasUserPermission

from . import filters, serializers


class ManageTrackFileViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = (
        music_models.TrackFile.objects.all()
        .select_related("track__artist", "track__album__artist")
        .order_by("-id")
    )
    serializer_class = serializers.ManageTrackFileSerializer
    filter_class = filters.ManageTrackFileFilterSet
    permission_classes = (HasUserPermission,)
    required_permissions = ["library"]
    ordering_fields = [
        "accessed_date",
        "modification_date",
        "creation_date",
        "track__artist__name",
        "bitrate",
        "size",
        "duration",
    ]

    @list_route(methods=["post"])
    def action(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = serializers.ManageTrackFileActionSerializer(
            request.data, queryset=queryset
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return response.Response(result, status=200)


class ManageUserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = users_models.User.objects.all().order_by("-id")
    serializer_class = serializers.ManageUserSerializer
    filter_class = filters.ManageUserFilterSet
    permission_classes = (HasUserPermission,)
    required_permissions = ["settings"]
    ordering_fields = ["date_joined", "last_activity", "username"]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["default_permissions"] = preferences.get("users__default_permissions")
        return context


class ManageInvitationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        users_models.Invitation.objects.all()
        .order_by("-id")
        .prefetch_related("users")
        .select_related("owner")
    )
    serializer_class = serializers.ManageInvitationSerializer
    filter_class = filters.ManageInvitationFilterSet
    permission_classes = (HasUserPermission,)
    required_permissions = ["settings"]
    ordering_fields = ["creation_date", "expiration_date"]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @list_route(methods=["post"])
    def action(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = serializers.ManageInvitationActionSerializer(
            request.data, queryset=queryset
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return response.Response(result, status=200)


class ManageImportRequestViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        requests_models.ImportRequest.objects.all()
        .order_by("-id")
        .select_related("user")
    )
    serializer_class = serializers.ManageImportRequestSerializer
    filter_class = filters.ManageImportRequestFilterSet
    permission_classes = (HasUserPermission,)
    required_permissions = ["library"]
    ordering_fields = ["creation_date", "imported_date"]

    @list_route(methods=["post"])
    def action(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = serializers.ManageImportRequestActionSerializer(
            request.data, queryset=queryset
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return response.Response(result, status=200)
