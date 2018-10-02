import logging
import urllib

from django.conf import settings
from django.db import transaction
from django.db.models import Count, Prefetch, Sum, F, Q
from django.db.models.functions import Length
from django.utils import timezone

from rest_framework import mixins
from rest_framework import permissions
from rest_framework import settings as rest_settings
from rest_framework import views, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from taggit.models import Tag

from funkwhale_api.common import utils as common_utils
from funkwhale_api.common import permissions as common_permissions
from funkwhale_api.federation.authentication import SignatureAuthentication
from funkwhale_api.federation import api_serializers as federation_api_serializers
from funkwhale_api.federation import routes

from . import filters, models, serializers, tasks, utils

logger = logging.getLogger(__name__)


def get_libraries(filter_uploads):
    def view(self, request, *args, **kwargs):
        obj = self.get_object()
        actor = utils.get_actor_from_request(request)
        uploads = models.Upload.objects.all()
        uploads = filter_uploads(obj, uploads)
        uploads = uploads.playable_by(actor)
        libraries = models.Library.objects.filter(
            pk__in=uploads.values_list("library", flat=True)
        )
        libraries = libraries.select_related("actor")
        page = self.paginate_queryset(libraries)
        if page is not None:
            serializer = federation_api_serializers.LibrarySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = federation_api_serializers.LibrarySerializer(libraries, many=True)
        return Response(serializer.data)

    return view


class TagViewSetMixin(object):
    def get_queryset(self):
        queryset = super().get_queryset()
        tag = self.request.query_params.get("tag")
        if tag:
            queryset = queryset.filter(tags__pk=tag)
        return queryset


class ArtistViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Artist.objects.all()
    serializer_class = serializers.ArtistWithAlbumsSerializer
    permission_classes = [common_permissions.ConditionalAuthentication]
    filter_class = filters.ArtistFilter
    ordering_fields = ("id", "name", "creation_date")

    def get_queryset(self):
        queryset = super().get_queryset()
        albums = models.Album.objects.with_tracks_count()
        albums = albums.annotate_playable_by_actor(
            utils.get_actor_from_request(self.request)
        )
        return queryset.prefetch_related(Prefetch("albums", queryset=albums)).distinct()

    libraries = detail_route(methods=["get"])(
        get_libraries(
            filter_uploads=lambda o, uploads: uploads.filter(
                Q(track__artist=o) | Q(track__album__artist=o)
            )
        )
    )


class AlbumViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        models.Album.objects.all().order_by("artist", "release_date").select_related()
    )
    serializer_class = serializers.AlbumSerializer
    permission_classes = [common_permissions.ConditionalAuthentication]
    ordering_fields = ("creation_date", "release_date", "title")
    filter_class = filters.AlbumFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        tracks = models.Track.objects.annotate_playable_by_actor(
            utils.get_actor_from_request(self.request)
        ).select_related("artist")
        if (
            hasattr(self, "kwargs")
            and self.kwargs
            and self.request.method.lower() == "get"
        ):
            # we are detailing a single album, so we can add the overhead
            # to fetch additional data
            tracks = tracks.annotate_duration()
        qs = queryset.prefetch_related(Prefetch("tracks", queryset=tracks))
        return qs.distinct()

    libraries = detail_route(methods=["get"])(
        get_libraries(filter_uploads=lambda o, uploads: uploads.filter(track__album=o))
    )


class LibraryViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = "uuid"
    queryset = (
        models.Library.objects.all()
        .order_by("-creation_date")
        .annotate(_uploads_count=Count("uploads"))
        .annotate(_size=Sum("uploads__size"))
    )
    serializer_class = serializers.LibraryForOwnerSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        common_permissions.OwnerPermission,
    ]
    owner_field = "actor.user"
    owner_checks = ["read", "write"]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(actor=self.request.user.actor)

    def perform_create(self, serializer):
        serializer.save(actor=self.request.user.actor)

    @transaction.atomic
    def perform_destroy(self, instance):
        routes.outbox.dispatch(
            {"type": "Delete", "object": {"type": "Library"}},
            context={"library": instance},
        )
        instance.delete()

    @detail_route(methods=["get"])
    @transaction.non_atomic_requests
    def follows(self, request, *args, **kwargs):
        library = self.get_object()
        queryset = (
            library.received_follows.filter(target__actor=self.request.user.actor)
            .select_related("actor", "target__actor")
            .order_by("-creation_date")
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = federation_api_serializers.LibraryFollowSerializer(
                page, many=True
            )
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TrackViewSet(TagViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """

    queryset = models.Track.objects.all().for_nested_serialization()
    serializer_class = serializers.TrackSerializer
    permission_classes = [common_permissions.ConditionalAuthentication]
    filter_class = filters.TrackFilter
    ordering_fields = (
        "creation_date",
        "title",
        "album__release_date",
        "size",
        "artist__name",
    )

    def get_queryset(self):
        queryset = super().get_queryset()
        filter_favorites = self.request.GET.get("favorites", None)
        user = self.request.user
        if user.is_authenticated and filter_favorites == "true":
            queryset = queryset.filter(track_favorites__user=user)

        queryset = queryset.annotate_playable_by_actor(
            utils.get_actor_from_request(self.request)
        ).annotate_duration()
        if (
            hasattr(self, "kwargs")
            and self.kwargs
            and self.request.method.lower() == "get"
        ):
            # we are detailing a single track, so we can add the overhead
            # to fetch additional data
            queryset = queryset.annotate_file_data()
        return queryset.distinct()

    @detail_route(methods=["get"])
    @transaction.non_atomic_requests
    def lyrics(self, request, *args, **kwargs):
        try:
            track = models.Track.objects.get(pk=kwargs["pk"])
        except models.Track.DoesNotExist:
            return Response(status=404)

        work = track.work
        if not work:
            work = track.get_work()

        if not work:
            return Response({"error": "unavailable work "}, status=404)

        lyrics = work.fetch_lyrics()
        try:
            if not lyrics.content:
                tasks.fetch_content(lyrics_id=lyrics.pk)
                lyrics.refresh_from_db()
        except AttributeError:
            return Response({"error": "unavailable lyrics"}, status=404)
        serializer = serializers.LyricsSerializer(lyrics)
        return Response(serializer.data)

    libraries = detail_route(methods=["get"])(
        get_libraries(filter_uploads=lambda o, uploads: uploads.filter(track=o))
    )


def get_file_path(audio_file):
    serve_path = settings.MUSIC_DIRECTORY_SERVE_PATH
    prefix = settings.MUSIC_DIRECTORY_PATH
    t = settings.REVERSE_PROXY_TYPE
    if t == "nginx":
        # we have to use the internal locations
        try:
            path = audio_file.url
        except AttributeError:
            # a path was given
            if not serve_path or not prefix:
                raise ValueError(
                    "You need to specify MUSIC_DIRECTORY_SERVE_PATH and "
                    "MUSIC_DIRECTORY_PATH to serve in-place imported files"
                )
            path = "/music" + audio_file.replace(prefix, "", 1)
        return (settings.PROTECT_FILES_PATH + path).encode("utf-8")
    if t == "apache2":
        try:
            path = audio_file.path
        except AttributeError:
            # a path was given
            if not serve_path or not prefix:
                raise ValueError(
                    "You need to specify MUSIC_DIRECTORY_SERVE_PATH and "
                    "MUSIC_DIRECTORY_PATH to serve in-place imported files"
                )
            path = audio_file.replace(prefix, serve_path, 1)
        return path.encode("utf-8")


def handle_serve(upload, user):
    f = upload
    # we update the accessed_date
    f.accessed_date = timezone.now()
    f.save(update_fields=["accessed_date"])

    if f.audio_file:
        file_path = get_file_path(f.audio_file)

    elif f.source and (
        f.source.startswith("http://") or f.source.startswith("https://")
    ):
        # we need to populate from cache
        with transaction.atomic():
            # why the transaction/select_for_update?
            # this is because browsers may send multiple requests
            # in a short time range, for partial content,
            # thus resulting in multiple downloads from the remote
            qs = f.__class__.objects.select_for_update()
            f = qs.get(pk=f.pk)
            f.download_audio_from_remote(user=user)
        data = f.get_audio_data()
        if data:
            f.duration = data["duration"]
            f.size = data["size"]
            f.bitrate = data["bitrate"]
            f.save(update_fields=["bitrate", "duration", "size"])
        file_path = get_file_path(f.audio_file)
    elif f.source and f.source.startswith("file://"):
        file_path = get_file_path(f.source.replace("file://", "", 1))
    mt = f.mimetype
    if mt:
        response = Response(content_type=mt)
    else:
        response = Response()
    filename = f.filename
    mapping = {"nginx": "X-Accel-Redirect", "apache2": "X-Sendfile"}
    file_header = mapping[settings.REVERSE_PROXY_TYPE]
    response[file_header] = file_path
    filename = "filename*=UTF-8''{}".format(urllib.parse.quote(filename))
    response["Content-Disposition"] = "attachment; {}".format(filename)
    if mt:
        response["Content-Type"] = mt

    return response


class ListenViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = models.Track.objects.all()
    serializer_class = serializers.TrackSerializer
    authentication_classes = (
        rest_settings.api_settings.DEFAULT_AUTHENTICATION_CLASSES
        + [SignatureAuthentication]
    )
    permission_classes = [common_permissions.ConditionalAuthentication]
    lookup_field = "uuid"

    def retrieve(self, request, *args, **kwargs):
        track = self.get_object()
        actor = utils.get_actor_from_request(request)
        queryset = track.uploads.select_related("track__album__artist", "track__artist")
        explicit_file = request.GET.get("upload")
        if explicit_file:
            queryset = queryset.filter(uuid=explicit_file)
        queryset = queryset.playable_by(actor)
        queryset = queryset.order_by(F("audio_file").desc(nulls_last=True))
        upload = queryset.first()
        if not upload:
            return Response(status=404)

        return handle_serve(upload, user=request.user)


class UploadViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = "uuid"
    queryset = (
        models.Upload.objects.all()
        .order_by("-creation_date")
        .select_related("library", "track__artist", "track__album__artist")
    )
    serializer_class = serializers.UploadForOwnerSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        common_permissions.OwnerPermission,
    ]
    owner_field = "library.actor.user"
    owner_checks = ["read", "write"]
    filter_class = filters.UploadFilter
    ordering_fields = (
        "creation_date",
        "import_date",
        "bitrate",
        "size",
        "artist__name",
    )

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(library__actor=self.request.user.actor)

    @list_route(methods=["post"])
    def action(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = serializers.UploadActionSerializer(request.data, queryset=queryset)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=200)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context

    def perform_create(self, serializer):
        upload = serializer.save()
        common_utils.on_commit(tasks.process_upload.delay, upload_id=upload.pk)

    @transaction.atomic
    def perform_destroy(self, instance):
        routes.outbox.dispatch(
            {"type": "Delete", "object": {"type": "Audio"}},
            context={"uploads": [instance]},
        )
        instance.delete()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all().order_by("name")
    serializer_class = serializers.TagSerializer
    permission_classes = [common_permissions.ConditionalAuthentication]


class Search(views.APIView):
    max_results = 3
    permission_classes = [common_permissions.ConditionalAuthentication]

    def get(self, request, *args, **kwargs):
        query = request.GET["query"]
        results = {
            # 'tags': serializers.TagSerializer(self.get_tags(query), many=True).data,
            "artists": serializers.ArtistWithAlbumsSerializer(
                self.get_artists(query), many=True
            ).data,
            "tracks": serializers.TrackSerializer(
                self.get_tracks(query), many=True
            ).data,
            "albums": serializers.AlbumSerializer(
                self.get_albums(query), many=True
            ).data,
        }
        return Response(results, status=200)

    def get_tracks(self, query):
        search_fields = [
            "mbid",
            "title__unaccent",
            "album__title__unaccent",
            "artist__name__unaccent",
        ]
        query_obj = utils.get_query(query, search_fields)
        return (
            models.Track.objects.all()
            .filter(query_obj)
            .select_related("artist", "album__artist")
        )[: self.max_results]

    def get_albums(self, query):
        search_fields = ["mbid", "title__unaccent", "artist__name__unaccent"]
        query_obj = utils.get_query(query, search_fields)
        return (
            models.Album.objects.all()
            .filter(query_obj)
            .select_related()
            .prefetch_related("tracks")
        )[: self.max_results]

    def get_artists(self, query):
        search_fields = ["mbid", "name__unaccent"]
        query_obj = utils.get_query(query, search_fields)
        return (models.Artist.objects.all().filter(query_obj).with_albums())[
            : self.max_results
        ]

    def get_tags(self, query):
        search_fields = ["slug", "name__unaccent"]
        query_obj = utils.get_query(query, search_fields)

        # We want the shortest tag first
        qs = (
            Tag.objects.all()
            .annotate(slug_length=Length("slug"))
            .order_by("slug_length")
        )

        return qs.filter(query_obj)[: self.max_results]
