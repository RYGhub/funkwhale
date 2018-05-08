from rest_framework import exceptions
from rest_framework import permissions as rest_permissions
from rest_framework import response
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.serializers import ValidationError

from funkwhale_api.music import models as music_models
from funkwhale_api.music import views as music_views

from . import authentication
from . import negotiation
from . import serializers


def find_object(queryset, model_field='pk', field='id', cast=int):
    def decorator(func):
        def inner(self, request, *args, **kwargs):
            data = request.GET or request.POST
            try:
                raw_value = data[field]
            except KeyError:
                return response.Response({
                    'code': 10,
                    'message': "required parameter '{}' not present".format(field)
                })
            try:
                value = cast(raw_value)
            except (TypeError, ValidationError):
                return response.Response({
                    'code': 0,
                    'message': 'For input string "{}"'.format(raw_value)
                })
            try:
                obj = queryset.get(**{model_field: value})
            except queryset.model.DoesNotExist:
                return response.Response({
                    'code': 70,
                    'message': '{} not found'.format(
                        queryset.model.__class__.__name__)
                })
            kwargs['obj'] = obj
            return func(self, request, *args, **kwargs)
        return inner
    return decorator


class SubsonicViewSet(viewsets.GenericViewSet):
    content_negotiation_class = negotiation.SubsonicContentNegociation
    authentication_classes = [authentication.SubsonicAuthentication]
    permissions_classes = [rest_permissions.IsAuthenticated]

    def handle_exception(self, exc):
        # subsonic API sends 200 status code with custom error
        # codes in the payload
        mapping = {
            exceptions.AuthenticationFailed: (
                40, 'Wrong username or password.'
            )
        }
        payload = {
            'status': 'failed'
        }
        try:
            code, message = mapping[exc.__class__]
        except KeyError:
            return super().handle_exception(exc)
        else:
            payload['error'] = {
                'code': code,
                'message': message
            }

        return response.Response(payload, status=200)

    @list_route(
        methods=['get', 'post'],
        permission_classes=[])
    def ping(self, request, *args, **kwargs):
        data = {
            'status': 'ok',
            'version': '1.16.0'
        }
        return response.Response(data, status=200)

    @list_route(
        methods=['get', 'post'],
        url_name='get_artists',
        url_path='getArtists')
    def get_artists(self, request, *args, **kwargs):
        artists = music_models.Artist.objects.all()
        data = serializers.GetArtistsSerializer(artists).data
        payload = {
            'artists': data
        }

        return response.Response(payload, status=200)

    @list_route(
        methods=['get', 'post'],
        url_name='get_artist',
        url_path='getArtist')
    @find_object(music_models.Artist.objects.all())
    def get_artist(self, request, *args, **kwargs):
        artist = kwargs.pop('obj')
        data = serializers.GetArtistSerializer(artist).data
        payload = {
            'artist': data
        }

        return response.Response(payload, status=200)

    @list_route(
        methods=['get', 'post'],
        url_name='get_album',
        url_path='getAlbum')
    @find_object(
        music_models.Album.objects.select_related('artist'))
    def get_album(self, request, *args, **kwargs):
        album = kwargs.pop('obj')
        data = serializers.GetAlbumSerializer(album).data
        payload = {
            'album': data
        }
        return response.Response(payload, status=200)

    @list_route(
        methods=['get', 'post'],
        url_name='stream',
        url_path='stream')
    @find_object(
        music_models.Track.objects.all())
    def stream(self, request, *args, **kwargs):
        track = kwargs.pop('obj')
        queryset = track.files.select_related(
            'library_track',
            'track__album__artist',
            'track__artist',
        )
        track_file = queryset.first()
        if not track_file:
            return Response(status=404)
        return music_views.handle_serve(track_file)
