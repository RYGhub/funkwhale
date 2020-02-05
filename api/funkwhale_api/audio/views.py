from rest_framework import decorators
from rest_framework import exceptions
from rest_framework import mixins
from rest_framework import permissions as rest_permissions
from rest_framework import response
from rest_framework import viewsets

from django import http
from django.db.models import Count, Prefetch
from django.db.utils import IntegrityError

from funkwhale_api.common import permissions
from funkwhale_api.common import preferences
from funkwhale_api.federation import models as federation_models
from funkwhale_api.music import models as music_models
from funkwhale_api.music import views as music_views
from funkwhale_api.users.oauth import permissions as oauth_permissions

from . import filters, models, renderers, serializers

ARTIST_PREFETCH_QS = (
    music_models.Artist.objects.select_related("description", "attachment_cover",)
    .prefetch_related(music_views.TAG_PREFETCH)
    .annotate(_tracks_count=Count("tracks"))
)


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
        .prefetch_related(
            "library",
            "attributed_to",
            "actor",
            Prefetch("artist", queryset=ARTIST_PREFETCH_QS),
        )
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

    @decorators.action(
        detail=True,
        methods=["get"],
        permission_classes=[],
        content_negotiation_class=renderers.PodcastRSSContentNegociation,
    )
    def rss(self, request, *args, **kwargs):
        object = self.get_object()
        uploads = (
            object.library.uploads.playable_by(None)
            .prefetch_related(
                Prefetch(
                    "track",
                    queryset=music_models.Track.objects.select_related(
                        "attachment_cover", "description"
                    ).prefetch_related(music_views.TAG_PREFETCH,),
                ),
            )
            .select_related("track__attachment_cover", "track__description")
            .order_by("-creation_date")
        )[:50]
        data = serializers.rss_serialize_channel_full(channel=object, uploads=uploads)
        return response.Response(data, status=200)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["subscriptions_count"] = self.action in [
            "retrieve",
            "create",
            "update",
            "partial_update",
        ]
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
            "actor",
            Prefetch("target__channel__artist", queryset=ARTIST_PREFETCH_QS),
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
        subscriptions = list(
            self.get_queryset().values_list("uuid", "target__channel__uuid")
        )

        payload = {
            "results": [{"uuid": str(u[0]), "channel": u[1]} for u in subscriptions],
            "count": len(subscriptions),
        }
        return response.Response(payload, status=200)
