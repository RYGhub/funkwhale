import requests.exceptions

from django.db import transaction
from django.db.models import Count

from rest_framework import decorators
from rest_framework import mixins
from rest_framework import permissions
from rest_framework import response
from rest_framework import viewsets

from funkwhale_api.music import models as music_models

from . import activity
from . import api_serializers
from . import filters
from . import models
from . import routes
from . import serializers
from . import utils


@transaction.atomic
def update_follow(follow, approved):
    follow.approved = approved
    follow.save(update_fields=["approved"])
    routes.outbox.dispatch({"type": "Accept"}, context={"follow": follow})


class LibraryFollowViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = "uuid"
    queryset = (
        models.LibraryFollow.objects.all()
        .order_by("-creation_date")
        .select_related("actor", "target__actor")
    )
    serializer_class = api_serializers.LibraryFollowSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_class = filters.LibraryFollowFilter
    ordering_fields = ("creation_date",)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(actor=self.request.user.actor)

    def perform_create(self, serializer):
        follow = serializer.save(actor=self.request.user.actor)
        routes.outbox.dispatch({"type": "Follow"}, context={"follow": follow})

    @transaction.atomic
    def perform_destroy(self, instance):
        routes.outbox.dispatch(
            {"type": "Undo", "object": {"type": "Follow"}}, context={"follow": instance}
        )
        instance.delete()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["actor"] = self.request.user.actor
        return context

    @decorators.detail_route(methods=["post"])
    def accept(self, request, *args, **kwargs):
        try:
            follow = self.queryset.get(
                target__actor=self.request.user.actor, uuid=kwargs["uuid"]
            )
        except models.LibraryFollow.DoesNotExist:
            return response.Response({}, status=404)
        update_follow(follow, approved=True)
        return response.Response(status=204)

    @decorators.detail_route(methods=["post"])
    def reject(self, request, *args, **kwargs):
        try:
            follow = self.queryset.get(
                target__actor=self.request.user.actor, uuid=kwargs["uuid"]
            )
        except models.LibraryFollow.DoesNotExist:
            return response.Response({}, status=404)

        update_follow(follow, approved=False)
        return response.Response(status=204)


class LibraryViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    lookup_field = "uuid"
    queryset = (
        music_models.Library.objects.all()
        .order_by("-creation_date")
        .select_related("actor__user")
        .annotate(_uploads_count=Count("uploads"))
    )
    serializer_class = api_serializers.LibrarySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.viewable_by(actor=self.request.user.actor)

    @decorators.detail_route(methods=["post"])
    def scan(self, request, *args, **kwargs):
        library = self.get_object()
        if library.actor.get_user():
            return response.Response({"status": "skipped"}, 200)

        scan = library.schedule_scan(actor=request.user.actor)
        if scan:
            return response.Response(
                {
                    "status": "scheduled",
                    "scan": api_serializers.LibraryScanSerializer(scan).data,
                },
                200,
            )
        return response.Response({"status": "skipped"}, 200)

    @decorators.list_route(methods=["post"])
    def fetch(self, request, *args, **kwargs):
        try:
            fid = request.data["fid"]
        except KeyError:
            return response.Response({"fid": ["This field is required"]})
        try:
            library = utils.retrieve(
                fid,
                queryset=self.queryset,
                serializer_class=serializers.LibrarySerializer,
            )
        except requests.exceptions.RequestException as e:
            return response.Response(
                {"detail": "Error while fetching the library: {}".format(str(e))},
                status=400,
            )
        except serializers.serializers.ValidationError as e:
            return response.Response(
                {"detail": "Invalid data in remote library: {}".format(str(e))},
                status=400,
            )
        serializer = self.serializer_class(library)
        return response.Response({"count": 1, "results": [serializer.data]})


class InboxItemViewSet(
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):

    queryset = (
        models.InboxItem.objects.select_related("activity__actor")
        .prefetch_related("activity__object", "activity__target")
        .filter(activity__type__in=activity.BROADCAST_TO_USER_ACTIVITIES, type="to")
        .order_by("-activity__creation_date")
    )
    serializer_class = api_serializers.InboxItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_class = filters.InboxItemFilter
    ordering_fields = ("activity__creation_date",)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(actor=self.request.user.actor)

    @decorators.list_route(methods=["post"])
    def action(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = api_serializers.InboxItemActionSerializer(
            request.data, queryset=queryset
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return response.Response(result, status=200)
