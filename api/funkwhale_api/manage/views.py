from rest_framework import mixins, response, viewsets
from rest_framework.decorators import list_route

from funkwhale_api.common import preferences
from funkwhale_api.music import models as music_models
from funkwhale_api.users import models as users_models
from funkwhale_api.users.permissions import HasUserPermission

from . import filters, serializers


class ManageTrackFileViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        music_models.TrackFile.objects.all()
        .select_related("track__artist", "track__album__artist", "library_track")
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
