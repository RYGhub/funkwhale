import ffmpeg
import os
import json
import logging
import subprocess
import unicodedata
import urllib

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.db import models, transaction
from django.db.models.functions import Length
from django.db.models import Count
from django.http import StreamingHttpResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator

from rest_framework import viewsets, views, mixins
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework import settings as rest_settings
from rest_framework import permissions
from musicbrainzngs import ResponseError

from funkwhale_api.common import utils as funkwhale_utils
from funkwhale_api.common.permissions import ConditionalAuthentication
from funkwhale_api.users.permissions import HasUserPermission
from taggit.models import Tag
from funkwhale_api.federation import actors
from funkwhale_api.federation.authentication import SignatureAuthentication
from funkwhale_api.federation.models import LibraryTrack
from funkwhale_api.musicbrainz import api
from funkwhale_api.requests.models import ImportRequest

from . import filters
from . import forms
from . import importers
from . import models
from . import permissions as music_permissions
from . import serializers
from . import tasks
from . import utils

logger = logging.getLogger(__name__)


class TagViewSetMixin(object):

    def get_queryset(self):
        queryset = super().get_queryset()
        tag = self.request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(tags__pk=tag)
        return queryset


class ArtistViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Artist.objects.with_albums()
    serializer_class = serializers.ArtistWithAlbumsSerializer
    permission_classes = [ConditionalAuthentication]
    filter_class = filters.ArtistFilter
    ordering_fields = ('id', 'name', 'creation_date')


class AlbumViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        models.Album.objects.all()
                            .order_by('artist', 'release_date')
                            .select_related()
                            .prefetch_related(
                                'tracks__artist',
                                'tracks__files'))
    serializer_class = serializers.AlbumSerializer
    permission_classes = [ConditionalAuthentication]
    ordering_fields = ('creation_date', 'release_date', 'title')
    filter_class = filters.AlbumFilter


class ImportBatchViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    queryset = (
        models.ImportBatch.objects
              .select_related()
              .order_by('-creation_date')
              .annotate(job_count=Count('jobs'))
    )
    serializer_class = serializers.ImportBatchSerializer
    permission_classes = (HasUserPermission,)
    required_permissions = ['library', 'upload']
    permission_operator = 'or'
    filter_class = filters.ImportBatchFilter

    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user)

    def get_queryset(self):
        qs = super().get_queryset()
        # if user do not have library permission, we limit to their
        # own jobs
        if not self.request.user.has_permissions('library'):
            qs = qs.filter(submitted_by=self.request.user)
        return qs


class ImportJobViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):
    queryset = (models.ImportJob.objects.all().select_related())
    serializer_class = serializers.ImportJobSerializer
    permission_classes = (HasUserPermission,)
    required_permissions = ['library', 'upload']
    permission_operator = 'or'
    filter_class = filters.ImportJobFilter

    def get_queryset(self):
        qs = super().get_queryset()
        # if user do not have library permission, we limit to their
        # own jobs
        if not self.request.user.has_permissions('library'):
            qs = qs.filter(batch__submitted_by=self.request.user)
        return qs

    @list_route(methods=['get'])
    def stats(self, request, *args, **kwargs):
        if not request.user.has_permissions('library'):
            return Response(status=403)
        qs = models.ImportJob.objects.all()
        filterset = filters.ImportJobFilter(request.GET, queryset=qs)
        qs = filterset.qs
        qs = qs.values('status').order_by('status')
        qs = qs.annotate(status_count=Count('status'))

        data = {}
        for row in qs:
            data[row['status']] = row['status_count']

        for s, _ in models.IMPORT_STATUS_CHOICES:
            data.setdefault(s, 0)

        data['count'] = sum([v for v in data.values()])
        return Response(data)

    @list_route(methods=['post'])
    def run(self, request, *args, **kwargs):
        serializer = serializers.ImportJobRunSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.save()

        return Response(payload)

    def perform_create(self, serializer):
        source = 'file://' + serializer.validated_data['audio_file'].name
        serializer.save(source=source)
        funkwhale_utils.on_commit(
            tasks.import_job_run.delay,
            import_job_id=serializer.instance.pk
        )


class TrackViewSet(TagViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = (models.Track.objects.all().for_nested_serialization())
    serializer_class = serializers.TrackSerializer
    permission_classes = [ConditionalAuthentication]
    filter_class = filters.TrackFilter
    ordering_fields = (
        'creation_date',
        'title',
        'album__title',
        'album__release_date',
        'position',
        'artist__name',
    )

    def get_queryset(self):
        queryset = super().get_queryset()
        filter_favorites = self.request.GET.get('favorites', None)
        user = self.request.user
        if user.is_authenticated and filter_favorites == 'true':
            queryset = queryset.filter(track_favorites__user=user)

        return queryset

    @detail_route(methods=['get'])
    @transaction.non_atomic_requests
    def lyrics(self, request, *args, **kwargs):
        try:
            track = models.Track.objects.get(pk=kwargs['pk'])
        except models.Track.DoesNotExist:
            return Response(status=404)

        work = track.work
        if not work:
            work = track.get_work()

        if not work:
            return Response({'error': 'unavailable work '}, status=404)

        lyrics = work.fetch_lyrics()
        try:
            if not lyrics.content:
                tasks.fetch_content(lyrics_id=lyrics.pk)
                lyrics.refresh_from_db()
        except AttributeError:
            return Response({'error': 'unavailable lyrics'}, status=404)
        serializer = serializers.LyricsSerializer(lyrics)
        return Response(serializer.data)


def get_file_path(audio_file):
    serve_path = settings.MUSIC_DIRECTORY_SERVE_PATH
    prefix = settings.MUSIC_DIRECTORY_PATH
    t = settings.REVERSE_PROXY_TYPE
    if t == 'nginx':
        # we have to use the internal locations
        try:
            path = audio_file.url
        except AttributeError:
            # a path was given
            if not serve_path or not prefix:
                raise ValueError(
                    'You need to specify MUSIC_DIRECTORY_SERVE_PATH and '
                    'MUSIC_DIRECTORY_PATH to serve in-place imported files'
                )
            path = '/music' + audio_file.replace(prefix, '', 1)
        return (settings.PROTECT_FILES_PATH + path).encode('utf-8')
    if t == 'apache2':
        try:
            path = audio_file.path
        except AttributeError:
            # a path was given
            if not serve_path or not prefix:
                raise ValueError(
                    'You need to specify MUSIC_DIRECTORY_SERVE_PATH and '
                    'MUSIC_DIRECTORY_PATH to serve in-place imported files'
                )
            path = audio_file.replace(prefix, serve_path, 1).encode('utf-8')
        return path


def handle_serve(track_file):
    f = track_file
    # we update the accessed_date
    f.accessed_date = timezone.now()
    f.save(update_fields=['accessed_date'])

    mt = f.mimetype
    audio_file = f.audio_file
    try:
        library_track = f.library_track
    except ObjectDoesNotExist:
        library_track = None
    if library_track and not audio_file:
        if not library_track.audio_file:
            # we need to populate from cache
            with transaction.atomic():
                # why the transaction/select_for_update?
                # this is because browsers may send multiple requests
                # in a short time range, for partial content,
                # thus resulting in multiple downloads from the remote
                qs = LibraryTrack.objects.select_for_update()
                library_track = qs.get(pk=library_track.pk)
                library_track.download_audio()
            track_file.library_track = library_track
            track_file.set_audio_data()
            track_file.save(update_fields=['bitrate', 'duration', 'size'])

        audio_file = library_track.audio_file
        file_path = get_file_path(audio_file)
        mt = library_track.audio_mimetype
    elif audio_file:
        file_path = get_file_path(audio_file)
    elif f.source and f.source.startswith('file://'):
        file_path = get_file_path(f.source.replace('file://', '', 1))
    if mt:
        response = Response(content_type=mt)
    else:
        response = Response()
    filename = f.filename
    mapping = {
        'nginx': 'X-Accel-Redirect',
        'apache2': 'X-Sendfile',
    }
    file_header = mapping[settings.REVERSE_PROXY_TYPE]
    response[file_header] = file_path
    filename = "filename*=UTF-8''{}".format(
        urllib.parse.quote(filename))
    response["Content-Disposition"] = "attachment; {}".format(filename)
    if mt:
        response["Content-Type"] = mt

    return response


class TrackFileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        models.TrackFile.objects.all()
            .select_related('track__artist', 'track__album')
            .order_by('-id')
    )
    serializer_class = serializers.TrackFileSerializer
    authentication_classes = rest_settings.api_settings.DEFAULT_AUTHENTICATION_CLASSES + [
        SignatureAuthentication
    ]
    permission_classes = [music_permissions.Listen]

    @detail_route(methods=['get'])
    def serve(self, request, *args, **kwargs):
        queryset = models.TrackFile.objects.select_related(
            'library_track',
            'track__album__artist',
            'track__artist',
        )
        try:
            return handle_serve(queryset.get(pk=kwargs['pk']))
        except models.TrackFile.DoesNotExist:
            return Response(status=404)

    @list_route(methods=['get'])
    def viewable(self, request, *args, **kwargs):
        return Response({}, status=200)

    @list_route(methods=['get'])
    def transcode(self, request, *args, **kwargs):
        form = forms.TranscodeForm(request.GET)
        if not form.is_valid():
            return Response(form.errors, status=400)

        f = form.cleaned_data['track_file']
        if not f.audio_file:
            return Response(status=400)
        output_kwargs = {
            'format': form.cleaned_data['to']
        }
        args = (ffmpeg
            .input(f.audio_file.path)
            .output('pipe:', **output_kwargs)
            .get_args()
        )
        # we use a generator here so the view return immediatly and send
        # file chunk to the browser, instead of blocking a few seconds
        def _transcode():
            p = subprocess.Popen(
                ['ffmpeg'] + args,
                stdout=subprocess.PIPE)
            for line in p.stdout:
                yield line

        response = StreamingHttpResponse(
            _transcode(), status=200,
            content_type=form.cleaned_data['to'])

        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = serializers.TagSerializer
    permission_classes = [ConditionalAuthentication]


class Search(views.APIView):
    max_results = 3
    permission_classes = [ConditionalAuthentication]

    def get(self, request, *args, **kwargs):
        query = request.GET['query']
        results = {
            # 'tags': serializers.TagSerializer(self.get_tags(query), many=True).data,
            'artists': serializers.ArtistWithAlbumsSerializer(self.get_artists(query), many=True).data,
            'tracks': serializers.TrackSerializer(self.get_tracks(query), many=True).data,
            'albums': serializers.AlbumSerializer(self.get_albums(query), many=True).data,
        }
        return Response(results, status=200)

    def get_tracks(self, query):
        search_fields = [
            'mbid',
            'title__unaccent',
            'album__title__unaccent',
            'artist__name__unaccent']
        query_obj = utils.get_query(query, search_fields)
        return (
            models.Track.objects.all()
                        .filter(query_obj)
                        .select_related('artist', 'album__artist')
                        .prefetch_related('files')
        )[:self.max_results]

    def get_albums(self, query):
        search_fields = [
            'mbid',
            'title__unaccent',
            'artist__name__unaccent']
        query_obj = utils.get_query(query, search_fields)
        return (
            models.Album.objects.all()
                        .filter(query_obj)
                        .select_related()
                        .prefetch_related(
                            'tracks__files',
                        )
        )[:self.max_results]

    def get_artists(self, query):
        search_fields = ['mbid', 'name__unaccent']
        query_obj = utils.get_query(query, search_fields)
        return (
            models.Artist.objects.all()
                         .filter(query_obj)
                         .with_albums()
        )[:self.max_results]

    def get_tags(self, query):
        search_fields = ['slug', 'name__unaccent']
        query_obj = utils.get_query(query, search_fields)

        # We want the shortest tag first
        qs = Tag.objects.all().annotate(slug_length=Length('slug')).order_by('slug_length')

        return qs.filter(query_obj)[:self.max_results]


class SubmitViewSet(viewsets.ViewSet):
    queryset = models.ImportBatch.objects.none()
    permission_classes = (HasUserPermission,)
    required_permissions = ['library']

    @list_route(methods=['post'])
    @transaction.non_atomic_requests
    def single(self, request, *args, **kwargs):
        try:
            models.Track.objects.get(mbid=request.POST['mbid'])
            return Response({})
        except models.Track.DoesNotExist:
            pass
        batch = models.ImportBatch.objects.create(submitted_by=request.user)
        job = models.ImportJob.objects.create(mbid=request.POST['mbid'], batch=batch, source=request.POST['import_url'])
        tasks.import_job_run.delay(import_job_id=job.pk)
        serializer = serializers.ImportBatchSerializer(batch)
        return Response(serializer.data, status=201)

    def get_import_request(self, data):
        try:
            raw = data['importRequest']
        except KeyError:
            return

        pk = int(raw)
        try:
            return ImportRequest.objects.get(pk=pk)
        except ImportRequest.DoesNotExist:
            pass

    @list_route(methods=['post'])
    @transaction.non_atomic_requests
    def album(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        import_request = self.get_import_request(data)
        import_data, batch = self._import_album(
            data, request, batch=None, import_request=import_request)
        return Response(import_data)

    @transaction.atomic
    def _import_album(self, data, request, batch=None, import_request=None):
        # we import the whole album here to prevent race conditions that occurs
        # when using get_or_create_from_api in tasks
        album_data = api.releases.get(id=data['releaseId'], includes=models.Album.api_includes)['release']
        cleaned_data = models.Album.clean_musicbrainz_data(album_data)
        album = importers.load(models.Album, cleaned_data, album_data, import_hooks=[models.import_tracks])
        try:
            album.get_image()
        except ResponseError:
            pass
        if not batch:
            batch = models.ImportBatch.objects.create(
                submitted_by=request.user,
                import_request=import_request)
        for row in data['tracks']:
            try:
                models.TrackFile.objects.get(track__mbid=row['mbid'])
            except models.TrackFile.DoesNotExist:
                job = models.ImportJob.objects.create(mbid=row['mbid'], batch=batch, source=row['source'])
                funkwhale_utils.on_commit(
                    tasks.import_job_run.delay,
                    import_job_id=job.pk
                )

        serializer = serializers.ImportBatchSerializer(batch)
        return serializer.data, batch

    @list_route(methods=['post'])
    @transaction.non_atomic_requests
    def artist(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        import_request = self.get_import_request(data)
        artist_data = api.artists.get(id=data['artistId'])['artist']
        cleaned_data = models.Artist.clean_musicbrainz_data(artist_data)
        artist = importers.load(models.Artist, cleaned_data, artist_data, import_hooks=[])

        import_data = []
        batch = None
        for row in data['albums']:
            row_data, batch = self._import_album(
                row, request, batch=batch, import_request=import_request)
            import_data.append(row_data)

        return Response(import_data[0])
