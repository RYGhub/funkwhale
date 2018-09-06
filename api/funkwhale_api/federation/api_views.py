import requests.exceptions

from django.db.models import Count

from rest_framework import decorators
from rest_framework import mixins
from rest_framework import permissions
from rest_framework import response
from rest_framework import viewsets

from funkwhale_api.music import models as music_models

from . import api_serializers
from . import filters
from . import models
from . import routes
from . import serializers
from . import utils


class LibraryFollowViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = "uuid"
    queryset = (
        models.LibraryFollow.objects.all()
        .order_by("-creation_date")
        .select_related("target__actor", "actor")
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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["actor"] = self.request.user.actor
        return context


class LibraryViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    lookup_field = "uuid"
    queryset = (
        music_models.Library.objects.all()
        .order_by("-creation_date")
        .select_related("actor")
        .annotate(_files_count=Count("files"))
    )
    serializer_class = api_serializers.LibrarySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_class = filters.LibraryFollowFilter
    ordering_fields = ("creation_date",)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.viewable_by(actor=self.request.user.actor)

    @decorators.list_route(methods=["post"])
    def scan(self, request, *args, **kwargs):
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
                {"detail": "Error while scanning the library: {}".format(str(e))},
                status=400,
            )
        except serializers.serializers.ValidationError as e:
            return response.Response(
                {"detail": "Invalid data in remote library: {}".format(str(e))},
                status=400,
            )
        serializer = self.serializer_class(library)
        return response.Response({"count": 1, "results": [serializer.data]})
