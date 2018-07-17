from django.db import transaction
from django.db.models import Count
from rest_framework import exceptions, mixins, viewsets
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from funkwhale_api.common import fields, permissions

from . import filters, models, serializers


class PlaylistViewSet(
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):

    serializer_class = serializers.PlaylistSerializer
    queryset = (
        models.Playlist.objects.all()
        .select_related("user")
        .annotate(tracks_count=Count("playlist_tracks"))
        .with_covers()
        .with_duration()
    )
    permission_classes = [
        permissions.ConditionalAuthentication,
        permissions.OwnerPermission,
        IsAuthenticatedOrReadOnly,
    ]
    owner_checks = ["write"]
    filter_class = filters.PlaylistFilter
    ordering_fields = ("id", "name", "creation_date", "modification_date")

    @detail_route(methods=["get"])
    def tracks(self, request, *args, **kwargs):
        playlist = self.get_object()
        plts = playlist.playlist_tracks.all().for_nested_serialization()
        serializer = serializers.PlaylistTrackSerializer(plts, many=True)
        data = {"count": len(plts), "results": serializer.data}
        return Response(data, status=200)

    @detail_route(methods=["post"])
    @transaction.atomic
    def add(self, request, *args, **kwargs):
        playlist = self.get_object()
        serializer = serializers.PlaylistAddManySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            plts = playlist.insert_many(serializer.validated_data["tracks"])
        except exceptions.ValidationError as e:
            payload = {"playlist": e.detail}
            return Response(payload, status=400)
        ids = [p.id for p in plts]
        plts = (
            models.PlaylistTrack.objects.filter(pk__in=ids)
            .order_by("index")
            .for_nested_serialization()
        )
        serializer = serializers.PlaylistTrackSerializer(plts, many=True)
        data = {"count": len(plts), "results": serializer.data}
        return Response(data, status=201)

    @detail_route(methods=["delete"])
    @transaction.atomic
    def clear(self, request, *args, **kwargs):
        playlist = self.get_object()
        playlist.playlist_tracks.all().delete()
        playlist.save(update_fields=["modification_date"])
        return Response(status=204)

    def get_queryset(self):
        return self.queryset.filter(fields.privacy_level_query(self.request.user))

    def perform_create(self, serializer):
        return serializer.save(
            user=self.request.user,
            privacy_level=serializer.validated_data.get(
                "privacy_level", self.request.user.privacy_level
            ),
        )


class PlaylistTrackViewSet(
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):

    serializer_class = serializers.PlaylistTrackSerializer
    queryset = models.PlaylistTrack.objects.all().for_nested_serialization()
    permission_classes = [
        permissions.ConditionalAuthentication,
        permissions.OwnerPermission,
        IsAuthenticatedOrReadOnly,
    ]
    owner_field = "playlist.user"
    owner_checks = ["write"]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH", "DELETE", "POST"]:
            return serializers.PlaylistTrackWriteSerializer
        return self.serializer_class

    def get_queryset(self):
        return self.queryset.filter(
            fields.privacy_level_query(
                self.request.user,
                lookup_field="playlist__privacy_level",
                user_field="playlist__user",
            )
        )

    def perform_destroy(self, instance):
        instance.delete(update_indexes=True)
