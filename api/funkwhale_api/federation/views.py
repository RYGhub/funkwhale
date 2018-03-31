from django import forms
from django.conf import settings
from django.http import HttpResponse

from rest_framework import viewsets
from rest_framework import views
from rest_framework import response
from rest_framework.decorators import list_route, detail_route

from . import actors
from . import renderers
from . import serializers
from . import webfinger


class FederationMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not settings.FEDERATION_ENABLED:
            return HttpResponse(status=405)
        return super().dispatch(request, *args, **kwargs)


class InstanceActorViewSet(FederationMixin, viewsets.GenericViewSet):
    lookup_field = 'actor'
    lookup_value_regex = '[a-z]*'
    authentication_classes = []
    permission_classes = []
    renderer_classes = [renderers.ActivityPubRenderer]

    def get_object(self):
        try:
            return actors.SYSTEM_ACTORS[self.kwargs['actor']]
        except KeyError:
            raise Http404

    def retrieve(self, request, *args, **kwargs):
        actor_conf = self.get_object()
        actor = actor_conf['get_actor']()
        serializer = serializers.ActorSerializer(actor)
        return response.Response(serializer.data, status=200)

    @detail_route(methods=['get'])
    def inbox(self, request, *args, **kwargs):
        raise NotImplementedError()

    @detail_route(methods=['get'])
    def outbox(self, request, *args, **kwargs):
        raise NotImplementedError()


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
        actor = actors.SYSTEM_ACTORS[username]['get_actor']()
        return serializers.ActorWebfingerSerializer(actor).data
