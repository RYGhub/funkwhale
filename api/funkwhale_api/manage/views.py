from rest_framework import mixins, response, viewsets
from rest_framework.decorators import detail_route, list_route

from funkwhale_api.common import preferences
from funkwhale_api.federation import models as federation_models
from funkwhale_api.federation import tasks as federation_tasks
from funkwhale_api.music import models as music_models
from funkwhale_api.users import models as users_models
from funkwhale_api.users.permissions import HasUserPermission

from . import filters, serializers


class ManageUploadViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = (
        music_models.Upload.objects.all()
        .select_related("track__artist", "track__album__artist")
        .order_by("-id")
    )
    serializer_class = serializers.ManageUploadSerializer
    filter_class = filters.ManageUploadFilterSet
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
        serializer = serializers.ManageUploadActionSerializer(
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


class ManageDomainViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    lookup_value_regex = r"[a-zA-Z0-9\-\.]+"
    queryset = (
        federation_models.Domain.objects.external()
        .with_last_activity_date()
        .with_actors_count()
        .with_outbox_activities_count()
        .order_by("name")
    )
    serializer_class = serializers.ManageDomainSerializer
    filter_class = filters.ManageDomainFilterSet
    permission_classes = (HasUserPermission,)
    required_permissions = ["moderation"]
    ordering_fields = [
        "name",
        "creation_date",
        "last_activity_date",
        "actors_count",
        "outbox_activities_count",
    ]

    @detail_route(methods=["get"])
    def nodeinfo(self, request, *args, **kwargs):
        domain = self.get_object()
        federation_tasks.update_domain_nodeinfo(domain_name=domain.name)
        domain.refresh_from_db()
        return response.Response(domain.nodeinfo, status=200)

    @detail_route(methods=["get"])
    def stats(self, request, *args, **kwargs):
        domain = self.get_object()
        return response.Response(domain.get_stats(), status=200)
