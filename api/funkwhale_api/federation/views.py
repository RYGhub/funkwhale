from django import forms
from django.conf import settings
from django.core import paginator
from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse

from rest_framework import mixins
from rest_framework import permissions as rest_permissions
from rest_framework import response
from rest_framework import views
from rest_framework import viewsets
from rest_framework.decorators import list_route, detail_route
from rest_framework.serializers import ValidationError

from funkwhale_api.common import utils as funkwhale_utils
from funkwhale_api.common.permissions import HasModelPermission
from funkwhale_api.music.models import TrackFile

from . import activity
from . import actors
from . import authentication
from . import filters
from . import library
from . import models
from . import permissions
from . import renderers
from . import serializers
from . import tasks
from . import utils
from . import webfinger


class FederationMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not settings.FEDERATION_ENABLED:
            return HttpResponse(status=405)
        return super().dispatch(request, *args, **kwargs)


class InstanceActorViewSet(FederationMixin, viewsets.GenericViewSet):
    lookup_field = 'actor'
    lookup_value_regex = '[a-z]*'
    authentication_classes = [
        authentication.SignatureAuthentication]
    permission_classes = []
    renderer_classes = [renderers.ActivityPubRenderer]

    def get_object(self):
        try:
            return actors.SYSTEM_ACTORS[self.kwargs['actor']]
        except KeyError:
            raise Http404

    def retrieve(self, request, *args, **kwargs):
        system_actor = self.get_object()
        actor = system_actor.get_actor_instance()
        data = actor.system_conf.serialize()
        return response.Response(data, status=200)

    @detail_route(methods=['get', 'post'])
    def inbox(self, request, *args, **kwargs):
        system_actor = self.get_object()
        handler = getattr(system_actor, '{}_inbox'.format(
            request.method.lower()
        ))

        try:
            data = handler(request.data, actor=request.actor)
        except NotImplementedError:
            return response.Response(status=405)
        return response.Response({}, status=200)

    @detail_route(methods=['get', 'post'])
    def outbox(self, request, *args, **kwargs):
        system_actor = self.get_object()
        handler = getattr(system_actor, '{}_outbox'.format(
            request.method.lower()
        ))
        try:
            data = handler(request.data, actor=request.actor)
        except NotImplementedError:
            return response.Response(status=405)
        return response.Response({}, status=200)


class WellKnownViewSet(FederationMixin, viewsets.GenericViewSet):
    authentication_classes = []
    permission_classes = []
    renderer_classes = [renderers.WebfingerRenderer]

    @list_route(methods=['get'])
    def webfinger(self, request, *args, **kwargs):
        try:
            resource_type, resource = webfinger.clean_resource(
                request.GET['resource'])
            cleaner = getattr(webfinger, 'clean_{}'.format(resource_type))
            result = cleaner(resource)
        except forms.ValidationError as e:
            return response.Response({
                'errors': {
                    'resource': e.message
                }
            }, status=400)
        except KeyError:
            return response.Response({
                'errors': {
                    'resource': 'This field is required',
                }
            }, status=400)

        handler = getattr(self, 'handler_{}'.format(resource_type))
        data = handler(result)

        return response.Response(data)

    def handler_acct(self, clean_result):
        username, hostname = clean_result
        actor = actors.SYSTEM_ACTORS[username].get_actor_instance()
        return serializers.ActorWebfingerSerializer(actor).data


class MusicFilesViewSet(FederationMixin, viewsets.GenericViewSet):
    authentication_classes = [
        authentication.SignatureAuthentication]
    permission_classes = [permissions.LibraryFollower]
    renderer_classes = [renderers.ActivityPubRenderer]

    def list(self, request, *args, **kwargs):
        page = request.GET.get('page')
        library = actors.SYSTEM_ACTORS['library'].get_actor_instance()
        qs = TrackFile.objects.order_by('-creation_date').select_related(
            'track__artist',
            'track__album__artist'
        ).filter(library_track__isnull=True)
        if page is None:
            conf = {
                'id': utils.full_url(reverse('federation:music:files-list')),
                'page_size': settings.FEDERATION_COLLECTION_PAGE_SIZE,
                'items': qs,
                'item_serializer': serializers.AudioSerializer,
                'actor': library,
            }
            serializer = serializers.PaginatedCollectionSerializer(conf)
            data = serializer.data
        else:
            try:
                page_number = int(page)
            except:
                return response.Response(
                    {'page': ['Invalid page number']}, status=400)
            p = paginator.Paginator(
                qs, settings.FEDERATION_COLLECTION_PAGE_SIZE)
            try:
                page = p.page(page_number)
                conf = {
                    'id': utils.full_url(reverse('federation:music:files-list')),
                    'page': page,
                    'item_serializer': serializers.AudioSerializer,
                    'actor': library,
                }
                serializer = serializers.CollectionPageSerializer(conf)
                data = serializer.data
            except paginator.EmptyPage:
                return response.Response(status=404)

        return response.Response(data)


class LibraryPermission(HasModelPermission):
    model = models.Library


class LibraryViewSet(
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):
    permission_classes = [LibraryPermission]
    queryset = models.Library.objects.all().select_related(
        'actor',
        'follow',
    )
    lookup_field = 'uuid'
    filter_class = filters.LibraryFilter
    serializer_class = serializers.APILibrarySerializer
    ordering_fields = (
        'id',
        'creation_date',
        'fetched_date',
        'actor__domain',
        'tracks_count',
    )

    @list_route(methods=['get'])
    def fetch(self, request, *args, **kwargs):
        account = request.GET.get('account')
        if not account:
            return response.Response(
                {'account': 'This field is mandatory'}, status=400)

        data = library.scan_from_account_name(account)
        return response.Response(data)

    @detail_route(methods=['post'])
    def scan(self, request, *args, **kwargs):
        library = self.get_object()
        serializer = serializers.APILibraryScanSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        result = tasks.scan_library.delay(
            library_id=library.pk,
            until=serializer.validated_data.get('until')
        )
        return response.Response({'task': result.id})

    @list_route(methods=['get'])
    def following(self, request, *args, **kwargs):
        library_actor = actors.SYSTEM_ACTORS['library'].get_actor_instance()
        queryset = models.Follow.objects.filter(
            actor=library_actor
        ).select_related(
            'target',
            'target',
        ).order_by('-creation_date')
        filterset = filters.FollowFilter(request.GET, queryset=queryset)
        serializer = serializers.APIFollowSerializer(filterset.qs, many=True)
        data = {
            'results': serializer.data,
            'count': len(filterset.qs),
        }
        return response.Response(data)

    @list_route(methods=['get'])
    def followers(self, request, *args, **kwargs):
        library_actor = actors.SYSTEM_ACTORS['library'].get_actor_instance()
        queryset = models.Follow.objects.filter(
            target=library_actor
        ).select_related(
            'target',
            'target',
        ).order_by('-creation_date')
        filterset = filters.FollowFilter(request.GET, queryset=queryset)
        serializer = serializers.APIFollowSerializer(filterset.qs, many=True)
        data = {
            'results': serializer.data,
            'count': len(filterset.qs),
        }
        return response.Response(data)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = serializers.APILibraryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        library = serializer.save()
        return response.Response(serializer.data, status=201)


class LibraryTrackViewSet(
        mixins.ListModelMixin,
        viewsets.GenericViewSet):
    permission_classes = [LibraryPermission]
    queryset = models.LibraryTrack.objects.all().select_related(
        'library__actor',
        'library__follow',
        'local_track_file',
    )
    filter_class = filters.LibraryTrackFilter
    serializer_class = serializers.APILibraryTrackSerializer
    ordering_fields = (
        'id',
        'artist_name',
        'title',
        'album_title',
        'creation_date',
        'modification_date',
        'fetched_date',
        'published_date',
    )
