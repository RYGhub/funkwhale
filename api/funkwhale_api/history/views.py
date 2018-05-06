from rest_framework import generics, mixins, viewsets
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import detail_route

from funkwhale_api.activity import record
from funkwhale_api.common.permissions import ConditionalAuthentication
from funkwhale_api.music.serializers import TrackSerializerNested

from . import models
from . import serializers


class ListeningViewSet(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):

    serializer_class = serializers.ListeningSerializer
    queryset = models.Listening.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        r = super().perform_create(serializer)
        record.send(serializer.instance)
        return r

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context
