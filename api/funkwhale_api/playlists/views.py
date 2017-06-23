from rest_framework import generics, mixins, viewsets
from rest_framework import status
from rest_framework.response import Response

from funkwhale_api.music.models import Track
from funkwhale_api.common.permissions import ConditionalAuthentication

from . import models
from . import serializers


class PlaylistViewSet(
        mixins.RetrieveModelMixin,
        mixins.CreateModelMixin,
        mixins.DestroyModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):

    serializer_class = serializers.PlaylistSerializer
    queryset = (models.Playlist.objects.all())
    permission_classes = [ConditionalAuthentication]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        serializer = self.get_serializer(instance=instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class PlaylistTrackViewSet(
        mixins.CreateModelMixin,
        mixins.DestroyModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):

    serializer_class = serializers.PlaylistTrackSerializer
    queryset = (models.PlaylistTrack.objects.all())
    permission_classes = [ConditionalAuthentication]

    def create(self, request, *args, **kwargs):
        serializer = serializers.PlaylistTrackCreateSerializer(
            data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        serializer = self.get_serializer(instance=instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        return self.queryset.filter(playlist__user=self.request.user)
