from rest_framework import decorators
from rest_framework import exceptions
from rest_framework import mixins
from rest_framework import permissions as rest_permissions
from rest_framework import response
from rest_framework import viewsets

from django import http
from django.db.utils import IntegrityError

from funkwhale_api.common import permissions
from funkwhale_api.common import preferences
from funkwhale_api.federation import models as federation_models
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

    @decorators.action(
        detail=True,
        methods=["post"],
        permission_classes=[rest_permissions.IsAuthenticated],
    )
    def subscribe(self, request, *args, **kwargs):
        object = self.get_object()
        subscription = federation_models.Follow(
            target=object.actor, approved=True, actor=request.user.actor,
        )
        subscription.fid = subscription.get_federation_id()
        try:
            subscription.save()
        except IntegrityError:
            # there's already a subscription for this actor/channel
            subscription = object.actor.received_follows.filter(
                actor=request.user.actor
            ).get()

        data = serializers.SubscriptionSerializer(subscription).data
        return response.Response(data, status=201)

    @decorators.action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[rest_permissions.IsAuthenticated],
    )
    def unsubscribe(self, request, *args, **kwargs):
        object = self.get_object()
        request.user.actor.emitted_follows.filter(target=object.actor).delete()
        return response.Response(status=204)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["subscriptions_count"] = self.action in ["retrieve", "create", "update"]
        return context


class SubscriptionsViewSet(
    ChannelsMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = "uuid"
    serializer_class = serializers.SubscriptionSerializer
    queryset = (
        federation_models.Follow.objects.exclude(target__channel__isnull=True)
        .prefetch_related(
            "target__channel__library",
            "target__channel__attributed_to",
            "target__channel__artist__description",
            "actor",
        )
        .order_by("-creation_date")
    )
    permission_classes = [
        oauth_permissions.ScopePermission,
        rest_permissions.IsAuthenticated,
    ]
    required_scope = "libraries"
    anonymous_policy = False

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(actor=self.request.user.actor)

    @decorators.action(methods=["get"], detail=False)
    def all(self, request, *args, **kwargs):
        """
        Return all the subscriptions of the current user, with only limited data
        to have a performant endpoint and avoid lots of queries just to display
        subscription status in the UI
        """
        subscriptions = list(self.get_queryset().values_list("uuid", flat=True))

        payload = {
            "results": [str(u) for u in subscriptions],
            "count": len(subscriptions),
        }
        return response.Response(payload, status=200)
