import os
import json
import unicodedata
import urllib
from django.urls import reverse
from django.db import models, transaction
from django.db.models.functions import Length
from django.conf import settings
from rest_framework import viewsets, views
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework import permissions
from musicbrainzngs import ResponseError
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from funkwhale_api.musicbrainz import api
from funkwhale_api.common.permissions import ConditionalAuthentication
from taggit.models import Tag

from . import models
from . import serializers
from . import importers
from . import filters
from . import utils


class SearchMixin(object):
    search_fields = []

    @list_route(methods=['get'])
    def search(self, request, *args, **kwargs):
        query = utils.get_query(request.GET['query'], self.search_fields)
        queryset = self.get_queryset().filter(query)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

class TagViewSetMixin(object):

    def get_queryset(self):
        queryset = super().get_queryset()
        tag = self.request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(tags__pk=tag)
        return queryset

class ArtistViewSet(SearchMixin, viewsets.ReadOnlyModelViewSet):
    queryset = (
        models.Artist.objects.all()
                             .prefetch_related(
                                'albums__tracks__files',
                                'albums__tracks__artist',
                                'albums__tracks__tags'))
    serializer_class = serializers.ArtistSerializerNested
    permission_classes = [ConditionalAuthentication]
    search_fields = ['name']
    filter_class = filters.ArtistFilter
    ordering_fields = ('id', 'name', 'creation_date')

class AlbumViewSet(SearchMixin, viewsets.ReadOnlyModelViewSet):
    queryset = (
        models.Album.objects.all()
                            .order_by('-creation_date')
                            .select_related()
                            .prefetch_related('tracks__tags',
                                              'tracks__files'))
    serializer_class = serializers.AlbumSerializerNested
    permission_classes = [ConditionalAuthentication]
    search_fields = ['title']
    ordering_fields = ('creation_date',)


class ImportBatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        models.ImportBatch.objects.all()
                          .prefetch_related('jobs__track_file')
                          .order_by('-creation_date'))
    serializer_class = serializers.ImportBatchSerializer

    def get_queryset(self):
        return super().get_queryset().filter(submitted_by=self.request.user)


class TrackViewSet(TagViewSetMixin, SearchMixin, viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = (models.Track.objects.all()
                                    .select_related()
                                    .select_related('album__artist')
                                    .prefetch_related(
                                        'tags',
                                        'files',
                                        'artist__albums__tracks__tags'))
    serializer_class = serializers.TrackSerializerNested
    permission_classes = [ConditionalAuthentication]
    search_fields = ['title', 'artist__name']
    ordering_fields = (
        'creation_date',
        'title',
        'album__title',
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
                lyrics.fetch_content()
        except AttributeError:
            return Response({'error': 'unavailable lyrics'}, status=404)
        serializer = serializers.LyricsSerializer(lyrics)
        return Response(serializer.data)


class TrackFileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (models.TrackFile.objects.all().order_by('-id'))
    serializer_class = serializers.TrackFileSerializer
    permission_classes = [ConditionalAuthentication]

    @detail_route(methods=['get'])
    def serve(self, request, *args, **kwargs):
        try:
            f = models.TrackFile.objects.get(pk=kwargs['pk'])
        except models.TrackFile.DoesNotExist:
            return Response(status=404)

        response = Response()
        filename = "filename*=UTF-8''{}".format(
            urllib.parse.quote(f.filename))
        response["Content-Disposition"] = "attachment; {}".format(filename)
        response['X-Accel-Redirect'] = "{}{}".format(
            settings.PROTECT_FILES_PATH,
            f.audio_file.url)
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = serializers.TagSerializer
    permission_classes = [ConditionalAuthentication]


class Search(views.APIView):
    max_results = 3

    def get(self, request, *args, **kwargs):
        query = request.GET['query']
        results = {
            'tags': serializers.TagSerializer(self.get_tags(query), many=True).data,
            'artists': serializers.ArtistSerializerNested(self.get_artists(query), many=True).data,
            'tracks': serializers.TrackSerializerNested(self.get_tracks(query), many=True).data,
            'albums': serializers.AlbumSerializerNested(self.get_albums(query), many=True).data,
        }
        return Response(results, status=200)

    def get_tracks(self, query):
        search_fields = ['mbid', 'title', 'album__title', 'artist__name']
        query_obj = utils.get_query(query, search_fields)
        return (
            models.Track.objects.all()
                        .filter(query_obj)
                        .select_related('album__artist')
                        .prefetch_related(
                            'tags',
                            'artist__albums__tracks__tags',
                            'files')
        )[:self.max_results]


    def get_albums(self, query):
        search_fields = ['mbid', 'title', 'artist__name']
        query_obj = utils.get_query(query, search_fields)
        return (
            models.Album.objects.all()
                        .filter(query_obj)
                        .select_related()
                        .prefetch_related(
                            'tracks__tags',
                            'tracks__files',
                            )
        )[:self.max_results]


    def get_artists(self, query):
        search_fields = ['mbid', 'name']
        query_obj = utils.get_query(query, search_fields)
        return (
            models.Artist.objects.all()
                         .filter(query_obj)
                         .select_related()
                         .prefetch_related(
                             'albums__tracks__tags',
                             'albums__tracks__files',
                             )

        )[:self.max_results]


    def get_tags(self, query):
        search_fields = ['slug', 'name']
        query_obj = utils.get_query(query, search_fields)

        # We want the shortest tag first
        qs = Tag.objects.all().annotate(slug_length=Length('slug')).order_by('slug_length')

        return qs.filter(query_obj)[:self.max_results]


class SubmitViewSet(viewsets.ViewSet):
    queryset = models.ImportBatch.objects.none()
    permission_classes = (permissions.DjangoModelPermissions, )

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
        job.run.delay()
        serializer = serializers.ImportBatchSerializer(batch)
        return Response(serializer.data)

    @list_route(methods=['post'])
    @transaction.non_atomic_requests
    def album(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        import_data, batch = self._import_album(data, request, batch=None)
        return Response(import_data)

    def _import_album(self, data, request, batch=None):
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
            batch = models.ImportBatch.objects.create(submitted_by=request.user)
        for row in data['tracks']:
            try:
                models.TrackFile.objects.get(track__mbid=row['mbid'])
            except models.TrackFile.DoesNotExist:
                job = models.ImportJob.objects.create(mbid=row['mbid'], batch=batch, source=row['source'])
                job.run.delay()
        serializer = serializers.ImportBatchSerializer(batch)
        return serializer.data, batch

    @list_route(methods=['post'])
    @transaction.non_atomic_requests
    def artist(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        artist_data = api.artists.get(id=data['artistId'])['artist']
        cleaned_data = models.Artist.clean_musicbrainz_data(artist_data)
        artist = importers.load(models.Artist, cleaned_data, artist_data, import_hooks=[])

        import_data = []
        batch = None
        for row in data['albums']:
            row_data, batch = self._import_album(row, request, batch=batch)
            import_data.append(row_data)

        return Response(import_data[0])
