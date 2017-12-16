from rest_framework import generics, mixins, viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import detail_route

from funkwhale_api.music.serializers import TrackSerializerNested
from funkwhale_api.common.permissions import ConditionalAuthentication

from . import models
from . import serializers

class RadioSessionViewSet(mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):

    serializer_class = serializers.RadioSessionSerializer
    queryset = models.RadioSession.objects.all()
    permission_classes = [ConditionalAuthentication]

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


class RadioSessionTrackViewSet(mixins.CreateModelMixin,
                               viewsets.GenericViewSet):
    serializer_class = serializers.RadioSessionTrackSerializer
    queryset = models.RadioSessionTrack.objects.all()
    permission_classes = [ConditionalAuthentication]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = serializer.validated_data['session']
        try:
            if request.user.is_authenticated:
                assert request.user == session.user
            else:
                assert request.session.session_key == session.session_key
        except AssertionError:
            return Response(status=status.HTTP_403_FORBIDDEN)
        track = session.radio.pick()
        session_track = session.session_tracks.all().latest('id')
        # self.perform_create(serializer)
        # dirty override here, since we use a different serializer for creation and detail
        serializer = self.serializer_class(instance=session_track, context=self.get_serializer_context())
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'create':
            return serializers.RadioSessionTrackSerializerCreate
        return super().get_serializer_class(*args, **kwargs)
