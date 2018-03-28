from django import forms
from django.conf import settings
from django.http import HttpResponse

from rest_framework import viewsets
from rest_framework import views
from rest_framework import response
from rest_framework.decorators import list_route

from . import serializers
from . import webfinger


class FederationMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not settings.FEDERATION_ENABLED:
            return HttpResponse(status=405)
        return super().dispatch(request, *args, **kwargs)


class InstanceViewSet(FederationMixin, viewsets.GenericViewSet):
    authentication_classes = []
    permission_classes = []

    @list_route(methods=['get'])
    def actor(self, request, *args, **kwargs):
        return response.Response(serializers.repr_instance_actor())

    @list_route(methods=['get'])
    def inbox(self, request, *args, **kwargs):
        raise NotImplementedError()

    @list_route(methods=['get'])
    def outbox(self, request, *args, **kwargs):
        raise NotImplementedError()


class WellKnownViewSet(FederationMixin, viewsets.GenericViewSet):
    authentication_classes = []
    permission_classes = []

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

        return response.Response(
            data,
            content_type='application/jrd+json; charset=utf-8')

    def handler_acct(self, clean_result):
        username, hostname = clean_result
        if username == 'service':
            return webfinger.serialize_system_acct()
        return {}
