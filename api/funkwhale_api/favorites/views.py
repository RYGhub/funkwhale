from rest_framework import generics, mixins, viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework import pagination
from rest_framework.decorators import list_route

from funkwhale_api.activity import record
from funkwhale_api.music.models import Track
from funkwhale_api.common.permissions import ConditionalAuthentication

from . import models
from . import serializers


class TrackFavoriteViewSet(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):

    serializer_class = serializers.UserTrackFavoriteSerializer
    queryset = (models.TrackFavorite.objects.all())
    permission_classes = [ConditionalAuthentication]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        serializer = self.get_serializer(instance=instance)
        headers = self.get_success_headers(serializer.data)
        record.send(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        track = Track.objects.get(pk=serializer.data['track'])
        favorite = models.TrackFavorite.add(track=track, user=self.request.user)
        return favorite

    @list_route(methods=['delete', 'post'])
    def remove(self, request, *args, **kwargs):
        try:
            pk = int(request.data['track'])
            favorite = request.user.track_favorites.get(track__pk=pk)
        except (AttributeError, ValueError, models.TrackFavorite.DoesNotExist):
            return Response({}, status=400)
        favorite.delete()
        return Response([], status=status.HTTP_204_NO_CONTENT)
