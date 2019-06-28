from rest_framework import mixins, response, viewsets
from rest_framework import decorators as rest_decorators

from django.db.models import Count, Prefetch, Q, Sum, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404

from funkwhale_api.common import models as common_models
from funkwhale_api.common import preferences, decorators
from funkwhale_api.favorites import models as favorites_models
from funkwhale_api.federation import models as federation_models
from funkwhale_api.federation import tasks as federation_tasks
from funkwhale_api.history import models as history_models
from funkwhale_api.music import models as music_models
from funkwhale_api.moderation import models as moderation_models
from funkwhale_api.playlists import models as playlists_models
from funkwhale_api.users import models as users_models


from . import filters, serializers


def get_stats(tracks, target):
    data = {}
    tracks = list(tracks.values_list("pk", flat=True))
    uploads = music_models.Upload.objects.filter(track__in=tracks)
    data["listenings"] = history_models.Listening.objects.filter(
        track__in=tracks
    ).count()
    data["mutations"] = common_models.Mutation.objects.get_for_target(target).count()
    data["playlists"] = (
        playlists_models.PlaylistTrack.objects.filter(track__in=tracks)
        .values_list("playlist", flat=True)
        .distinct()
        .count()
    )
    data["track_favorites"] = favorites_models.TrackFavorite.objects.filter(
        track__in=tracks
    ).count()
    data["libraries"] = uploads.values_list("library", flat=True).distinct().count()
    data["uploads"] = uploads.count()
    data.update(get_media_stats(uploads))
    return data


def get_media_stats(uploads):
    data = {}
    data["media_total_size"] = uploads.aggregate(v=Sum("size"))["v"] or 0
    data["media_downloaded_size"] = (
        uploads.with_file().aggregate(v=Sum("size"))["v"] or 0
    )
    return data


class ManageArtistViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        music_models.Artist.objects.all()
        .order_by("-id")
        .select_related("attributed_to")
        .prefetch_related(
            "tracks",
            Prefetch(
                "albums",
                queryset=music_models.Album.objects.annotate(
                    tracks_count=Count("tracks")
                ),
            ),
        )
    )
    serializer_class = serializers.ManageArtistSerializer
    filterset_class = filters.ManageArtistFilterSet
    required_scope = "instance:libraries"
    ordering_fields = ["creation_date", "name"]

    @rest_decorators.action(methods=["get"], detail=True)
    def stats(self, request, *args, **kwargs):
        artist = self.get_object()
        tracks = music_models.Track.objects.filter(
            Q(artist=artist) | Q(album__artist=artist)
        )
        data = get_stats(tracks, artist)
        return response.Response(data, status=200)

    @rest_decorators.action(methods=["post"], detail=False)
    def action(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = serializers.ManageArtistActionSerializer(
            request.data, queryset=queryset
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return response.Response(result, status=200)


class ManageAlbumViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        music_models.Album.objects.all()
        .order_by("-id")
        .select_related("attributed_to", "artist")
        .prefetch_related("tracks")
    )
    serializer_class = serializers.ManageAlbumSerializer
    filterset_class = filters.ManageAlbumFilterSet
    required_scope = "instance:libraries"
    ordering_fields = ["creation_date", "title", "release_date"]

    @rest_decorators.action(methods=["get"], detail=True)
    def stats(self, request, *args, **kwargs):
        album = self.get_object()
        data = get_stats(album.tracks.all(), album)
        return response.Response(data, status=200)

    @rest_decorators.action(methods=["post"], detail=False)
    def action(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = serializers.ManageAlbumActionSerializer(
            request.data, queryset=queryset
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return response.Response(result, status=200)


uploads_subquery = (
    music_models.Upload.objects.filter(track_id=OuterRef("pk"))
    .order_by()
    .values("track_id")
    .annotate(track_count=Count("track_id"))
    .values("track_count")
)


class ManageTrackViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        music_models.Track.objects.all()
        .order_by("-id")
        .select_related("attributed_to", "artist", "album__artist")
        .annotate(uploads_count=Coalesce(Subquery(uploads_subquery), 0))
    )
    serializer_class = serializers.ManageTrackSerializer
    filterset_class = filters.ManageTrackFilterSet
    required_scope = "instance:libraries"
    ordering_fields = [
        "creation_date",
        "title",
        "album__release_date",
        "position",
        "disc_number",
    ]

    @rest_decorators.action(methods=["get"], detail=True)
    def stats(self, request, *args, **kwargs):
        track = self.get_object()
        data = get_stats(track.__class__.objects.filter(pk=track.pk), track)
        return response.Response(data, status=200)

    @rest_decorators.action(methods=["post"], detail=False)
    def action(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = serializers.ManageTrackActionSerializer(
            request.data, queryset=queryset
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return response.Response(result, status=200)


uploads_subquery = (
    music_models.Upload.objects.filter(library_id=OuterRef("pk"))
    .order_by()
    .values("library_id")
    .annotate(library_count=Count("library_id"))
    .values("library_count")
)

follows_subquery = (
    federation_models.LibraryFollow.objects.filter(target_id=OuterRef("pk"))
    .order_by()
    .values("target_id")
    .annotate(library_count=Count("target_id"))
    .values("library_count")
)


class ManageLibraryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = "uuid"
    queryset = (
        music_models.Library.objects.all()
        .order_by("-id")
        .select_related("actor")
        .annotate(
            followers_count=Coalesce(Subquery(follows_subquery), 0),
            _uploads_count=Coalesce(Subquery(uploads_subquery), 0),
        )
    )
    serializer_class = serializers.ManageLibrarySerializer
    filterset_class = filters.ManageLibraryFilterSet
    required_scope = "instance:libraries"

    @rest_decorators.action(methods=["get"], detail=True)
    def stats(self, request, *args, **kwargs):
        library = self.get_object()
        uploads = library.uploads.all()
        tracks = uploads.values_list("track", flat=True).distinct()
        albums = (
            music_models.Track.objects.filter(pk__in=tracks)
            .values_list("album", flat=True)
            .distinct()
        )
        artists = set(
            music_models.Album.objects.filter(pk__in=albums).values_list(
                "artist", flat=True
            )
        ) | set(
            music_models.Track.objects.filter(pk__in=tracks).values_list(
                "artist", flat=True
            )
        )

        data = {
            "uploads": uploads.count(),
            "followers": library.received_follows.count(),
            "tracks": tracks.count(),
            "albums": albums.count(),
            "artists": len(artists),
        }
        data.update(get_media_stats(uploads.all()))
        return response.Response(data, status=200)

    @rest_decorators.action(methods=["post"], detail=False)
    def action(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = serializers.ManageTrackActionSerializer(
            request.data, queryset=queryset
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return response.Response(result, status=200)


class ManageUploadViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = "uuid"
    queryset = (
        music_models.Upload.objects.all()
        .order_by("-id")
        .select_related("library__actor", "track__artist", "track__album__artist")
    )
    serializer_class = serializers.ManageUploadSerializer
    filterset_class = filters.ManageUploadFilterSet
    required_scope = "instance:libraries"

    @rest_decorators.action(methods=["post"], detail=False)
    def action(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = serializers.ManageUploadActionSerializer(
            request.data, queryset=queryset
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return response.Response(result, status=200)


class ManageUserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = users_models.User.objects.all().select_related("actor").order_by("-id")
    serializer_class = serializers.ManageUserSerializer
    filterset_class = filters.ManageUserFilterSet
    required_scope = "instance:users"
    ordering_fields = ["date_joined", "last_activity", "username"]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["default_permissions"] = preferences.get("users__default_permissions")
        return context


class ManageInvitationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        users_models.Invitation.objects.all()
        .order_by("-id")
        .prefetch_related("users")
        .select_related("owner")
    )
    serializer_class = serializers.ManageInvitationSerializer
    filterset_class = filters.ManageInvitationFilterSet
    required_scope = "instance:invitations"
    ordering_fields = ["creation_date", "expiration_date"]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @rest_decorators.action(methods=["post"], detail=False)
    def action(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = serializers.ManageInvitationActionSerializer(
            request.data, queryset=queryset
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return response.Response(result, status=200)


class ManageDomainViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    lookup_value_regex = r"[a-zA-Z0-9\-\.]+"
    queryset = (
        federation_models.Domain.objects.external()
        .with_actors_count()
        .with_outbox_activities_count()
        .prefetch_related("instance_policy")
        .order_by("name")
    )
    serializer_class = serializers.ManageDomainSerializer
    filterset_class = filters.ManageDomainFilterSet
    required_scope = "instance:domains"
    ordering_fields = [
        "name",
        "creation_date",
        "nodeinfo_fetch_date",
        "actors_count",
        "outbox_activities_count",
        "instance_policy",
    ]

    def perform_create(self, serializer):
        domain = serializer.save()
        federation_tasks.update_domain_nodeinfo(domain_name=domain.name)

    @rest_decorators.action(methods=["get"], detail=True)
    def nodeinfo(self, request, *args, **kwargs):
        domain = self.get_object()
        federation_tasks.update_domain_nodeinfo(domain_name=domain.name)
        domain.refresh_from_db()
        return response.Response(domain.nodeinfo, status=200)

    @rest_decorators.action(methods=["get"], detail=True)
    def stats(self, request, *args, **kwargs):
        domain = self.get_object()
        return response.Response(domain.get_stats(), status=200)

    action = decorators.action_route(serializers.ManageDomainActionSerializer)


class ManageActorViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    lookup_value_regex = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
    queryset = (
        federation_models.Actor.objects.all()
        .with_uploads_count()
        .order_by("-creation_date")
        .select_related("user")
        .prefetch_related("instance_policy")
    )
    serializer_class = serializers.ManageActorSerializer
    filterset_class = filters.ManageActorFilterSet
    required_scope = "instance:accounts"
    required_permissions = ["moderation"]
    ordering_fields = [
        "name",
        "preferred_username",
        "domain",
        "fid",
        "creation_date",
        "last_fetch_date",
        "uploads_count",
        "outbox_activities_count",
        "instance_policy",
    ]

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        username, domain = self.kwargs["pk"].split("@")
        filter_kwargs = {"domain_id": domain, "preferred_username": username}
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)

        return obj

    @rest_decorators.action(methods=["get"], detail=True)
    def stats(self, request, *args, **kwargs):
        domain = self.get_object()
        return response.Response(domain.get_stats(), status=200)

    action = decorators.action_route(serializers.ManageActorActionSerializer)


class ManageInstancePolicyViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        moderation_models.InstancePolicy.objects.all()
        .order_by("-creation_date")
        .select_related()
    )
    serializer_class = serializers.ManageInstancePolicySerializer
    filterset_class = filters.ManageInstancePolicyFilterSet
    required_scope = "instance:policies"
    ordering_fields = ["id", "creation_date"]

    def perform_create(self, serializer):
        serializer.save(actor=self.request.user.actor)
