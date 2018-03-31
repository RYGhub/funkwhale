from django.db.models import Q
from django.http import Http404

from rest_framework import generics, mixins, viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route

from funkwhale_api.music.serializers import TrackSerializerNested
from funkwhale_api.common.permissions import ConditionalAuthentication

from . import models
from . import filters
from . import filtersets
from . import serializers


class RadioViewSet(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.ListModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):

    serializer_class = serializers.RadioSerializer
    permission_classes = [ConditionalAuthentication]
    filter_class = filtersets.RadioFilter

    def get_queryset(self):
        query = Q(is_public=True)
        if self.request.user.is_authenticated:
            query |= Q(user=self.request.user)
        return models.Radio.objects.filter(query)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise Http404
        return serializer.save(user=self.request.user)

    @detail_route(methods=['get'])
    def tracks(self, request, *args, **kwargs):
        radio = self.get_object()
        tracks = radio.get_candidates().for_nested_serialization()

        page = self.paginate_queryset(tracks)
        if page is not None:
            serializer = TrackSerializerNested(page, many=True)
            return self.get_paginated_response(serializer.data)

    @list_route(methods=['get'])
    def filters(self, request, *args, **kwargs):
        serializer = serializers.FilterSerializer(
            filters.registry.exposed_filters, many=True)
        return Response(serializer.data)

    @list_route(methods=['post'])
    def validate(self, request, *args, **kwargs):
        try:
            f_list = request.data['filters']
        except KeyError:
            return Response(
                {'error': 'You must provide a filters list'}, status=400)
        data = {
            'filters': []
        }
        for f in f_list:
            results = filters.test(f)
            if results['candidates']['sample']:
                qs = results['candidates']['sample'].for_nested_serialization()
                results['candidates']['sample'] = TrackSerializerNested(
                    qs, many=True).data
            data['filters'].append(results)

        return Response(data)


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
