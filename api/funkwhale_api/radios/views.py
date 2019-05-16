from django.db.models import Q
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from funkwhale_api.common import permissions as common_permissions
from funkwhale_api.music.serializers import TrackSerializer
from funkwhale_api.music import utils as music_utils
from funkwhale_api.users.oauth import permissions as oauth_permissions

from . import filters, filtersets, models, serializers


class RadioViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):

    serializer_class = serializers.RadioSerializer
    permission_classes = [
        oauth_permissions.ScopePermission,
        common_permissions.OwnerPermission,
    ]
    filterset_class = filtersets.RadioFilter
    required_scope = "radios"
    owner_field = "user"
    owner_checks = ["write"]
    anonymous_policy = "setting"

    def get_queryset(self):
        queryset = models.Radio.objects.all()
        query = Q(is_public=True)
        if self.request.user.is_authenticated:
            query |= Q(user=self.request.user)
        return queryset.filter(query)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        return serializer.save(user=self.request.user)

    @action(methods=["get"], detail=True)
    def tracks(self, request, *args, **kwargs):
        radio = self.get_object()
        tracks = radio.get_candidates().for_nested_serialization()
        actor = music_utils.get_actor_from_request(self.request)
        tracks = tracks.with_playable_uploads(actor)
        tracks = tracks.playable_by(actor)
        page = self.paginate_queryset(tracks)
        if page is not None:
            serializer = TrackSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    @action(methods=["get"], detail=False)
    def filters(self, request, *args, **kwargs):
        serializer = serializers.FilterSerializer(
            filters.registry.exposed_filters, many=True
        )
        return Response(serializer.data)

    @action(methods=["post"], detail=False)
    def validate(self, request, *args, **kwargs):
        try:
            f_list = request.data["filters"]
        except KeyError:
            return Response({"error": "You must provide a filters list"}, status=400)
        data = {"filters": []}
        for f in f_list:
            results = filters.test(f)
            if results["candidates"]["sample"]:
                qs = results["candidates"]["sample"].for_nested_serialization()
                results["candidates"]["sample"] = TrackSerializer(qs, many=True).data
            data["filters"].append(results)

        return Response(data)


class RadioSessionViewSet(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):

    serializer_class = serializers.RadioSessionSerializer
    queryset = models.RadioSession.objects.all()
    permission_classes = []

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            return queryset.filter(
                Q(user=self.request.user)
                | Q(session_key=self.request.session.session_key)
            )

        return queryset.filter(session_key=self.request.session.session_key).exclude(
            session_key=None
        )

    def perform_create(self, serializer):
        if (
            not self.request.user.is_authenticated
            and not self.request.session.session_key
        ):
            self.request.session.create()
        return serializer.save(
            user=self.request.user if self.request.user.is_authenticated else None,
            session_key=self.request.session.session_key,
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = (
            self.request.user if self.request.user.is_authenticated else None
        )
        return context


class RadioSessionTrackViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.RadioSessionTrackSerializer
    queryset = models.RadioSessionTrack.objects.all()
    permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = serializer.validated_data["session"]
        if not request.user.is_authenticated and not request.session.session_key:
            self.request.session.create()
        try:
            assert (request.user == session.user) or (
                request.session.session_key == session.session_key
                and session.session_key
            )
        except AssertionError:
            return Response(status=status.HTTP_403_FORBIDDEN)
        session.radio.pick()
        session_track = session.session_tracks.all().latest("id")
        # self.perform_create(serializer)
        # dirty override here, since we use a different serializer for creation and detail
        serializer = self.serializer_class(
            instance=session_track, context=self.get_serializer_context()
        )
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def get_serializer_class(self, *args, **kwargs):
        if self.action == "create":
            return serializers.RadioSessionTrackSerializerCreate
        return super().get_serializer_class(*args, **kwargs)
