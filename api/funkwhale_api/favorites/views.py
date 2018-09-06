from rest_framework import mixins, status, viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from django.db.models import Prefetch

from funkwhale_api.activity import record
from funkwhale_api.common import fields, permissions
from funkwhale_api.music.models import Track
from funkwhale_api.music import utils as music_utils

from . import filters, models, serializers


class TrackFavoriteViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):

    filter_class = filters.TrackFavoriteFilter
    serializer_class = serializers.UserTrackFavoriteSerializer
    queryset = models.TrackFavorite.objects.all().select_related("user")
    permission_classes = [
        permissions.ConditionalAuthentication,
        permissions.OwnerPermission,
        IsAuthenticatedOrReadOnly,
    ]
    owner_checks = ["write"]

    def get_serializer_class(self):
        if self.request.method.lower() in ["head", "get", "options"]:
            return serializers.UserTrackFavoriteSerializer
        return serializers.UserTrackFavoriteWriteSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        serializer = self.get_serializer(instance=instance)
        headers = self.get_success_headers(serializer.data)
        record.send(instance)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
            fields.privacy_level_query(self.request.user, "user__privacy_level")
        )
        tracks = Track.objects.annotate_playable_by_actor(
            music_utils.get_actor_from_request(self.request)
        ).select_related("artist", "album__artist")
        queryset = queryset.prefetch_related(Prefetch("track", queryset=tracks))
        return queryset

    def perform_create(self, serializer):
        track = Track.objects.get(pk=serializer.data["track"])
        favorite = models.TrackFavorite.add(track=track, user=self.request.user)
        return favorite

    @list_route(methods=["delete", "post"])
    def remove(self, request, *args, **kwargs):
        try:
            pk = int(request.data["track"])
            favorite = request.user.track_favorites.get(track__pk=pk)
        except (AttributeError, ValueError, models.TrackFavorite.DoesNotExist):
            return Response({}, status=400)
        favorite.delete()
        return Response([], status=status.HTTP_204_NO_CONTENT)
