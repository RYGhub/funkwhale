from rest_framework import generics, mixins, viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from funkwhale_api.music.models import Track
from funkwhale_api.common import permissions
from funkwhale_api.common import fields

from . import models
from . import serializers


class PlaylistViewSet(
        mixins.RetrieveModelMixin,
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):

    serializer_class = serializers.PlaylistSerializer
    queryset = (models.Playlist.objects.all())
    permission_classes = [
        permissions.ConditionalAuthentication,
        permissions.OwnerPermission,
        IsAuthenticatedOrReadOnly,
    ]

    def get_queryset(self):
        return self.queryset.filter(
            fields.privacy_level_query(self.request.user))

    def perform_create(self, serializer):
        return serializer.save(
            user=self.request.user,
            privacy_level=serializer.validated_data.get(
                'privacy_level', self.request.user.privacy_level)

        )


class PlaylistTrackViewSet(
        mixins.RetrieveModelMixin,
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):

    serializer_class = serializers.PlaylistTrackSerializer
    queryset = (models.PlaylistTrack.objects.all())
    permission_classes = [
        permissions.ConditionalAuthentication,
        permissions.OwnerPermission,
        IsAuthenticatedOrReadOnly,
    ]

    def create(self, request, *args, **kwargs):
        serializer = serializers.PlaylistTrackCreateSerializer(
            data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data['playlist'].user != request.user:
            return Response(
                {'playlist': [
                    'This playlist does not exists or you do not have the'
                    'permission to edit it']
                },
                status=400)
        instance = self.perform_create(serializer)
        serializer = self.get_serializer(instance=instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        return self.queryset.filter(
            fields.privacy_level_query(
                self.request.user,
                lookup_field='playlist__privacy_level'))
