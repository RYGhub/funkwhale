from rest_framework import generics, mixins, viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import detail_route

from funkwhale_api.activity import record
from funkwhale_api.common.permissions import ConditionalAuthentication
from funkwhale_api.music.serializers import TrackSerializerNested

from . import models
from . import serializers

class ListeningViewSet(mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):

    serializer_class = serializers.ListeningSerializer
    queryset = models.Listening.objects.all()
    permission_classes = [ConditionalAuthentication]

    def perform_create(self, serializer):
        r = super().perform_create(serializer)
        if self.request.user.is_authenticated:
            record.send(serializer.instance)
        return r

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            return queryset.filter(user=self.request.user)
        else:
            return queryset.filter(session_key=self.request.session.session_key)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.user.is_authenticated:
            context['user'] = self.request.user
        else:
            context['session_key'] = self.request.session.session_key
        return context
