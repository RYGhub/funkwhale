from django import forms
from django.core import paginator
from django.http import HttpResponse, Http404
from django.urls import reverse
from rest_framework import exceptions, mixins, response, viewsets
from rest_framework.decorators import detail_route, list_route

from funkwhale_api.common import preferences
from funkwhale_api.music import models as music_models

from . import (
    activity,
    actors,
    authentication,
    models,
    renderers,
    serializers,
    utils,
    webfinger,
)


class FederationMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not preferences.get("federation__enabled"):
            return HttpResponse(status=405)
        return super().dispatch(request, *args, **kwargs)


class ActorViewSet(FederationMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    lookup_field = "preferred_username"
    authentication_classes = [authentication.SignatureAuthentication]
    permission_classes = []
    renderer_classes = [renderers.ActivityPubRenderer]
    queryset = models.Actor.objects.local().select_related("user")
    serializer_class = serializers.ActorSerializer

    @detail_route(methods=["get", "post"])
    def inbox(self, request, *args, **kwargs):
        if request.method.lower() == "post" and request.actor is None:
            raise exceptions.AuthenticationFailed(
                "You need a valid signature to send an activity"
            )
        if request.method.lower() == "post":
            activity.receive(activity=request.data, on_behalf_of=request.actor)
        return response.Response({}, status=200)

    @detail_route(methods=["get", "post"])
    def outbox(self, request, *args, **kwargs):
        return response.Response({}, status=200)


class InstanceActorViewSet(FederationMixin, viewsets.GenericViewSet):
    lookup_field = "actor"
    lookup_value_regex = "[a-z]*"
    authentication_classes = [authentication.SignatureAuthentication]
    permission_classes = []
    renderer_classes = [renderers.ActivityPubRenderer]

    def get_object(self):
        try:
            return actors.SYSTEM_ACTORS[self.kwargs["actor"]]
        except KeyError:
            raise Http404

    def retrieve(self, request, *args, **kwargs):
        system_actor = self.get_object()
        actor = system_actor.get_actor_instance()
        data = actor.system_conf.serialize()
        return response.Response(data, status=200)

    @detail_route(methods=["get", "post"])
    def inbox(self, request, *args, **kwargs):
        system_actor = self.get_object()
        handler = getattr(system_actor, "{}_inbox".format(request.method.lower()))

        try:
            handler(request.data, actor=request.actor)
        except NotImplementedError:
            return response.Response(status=405)
        return response.Response({}, status=200)

    @detail_route(methods=["get", "post"])
    def outbox(self, request, *args, **kwargs):
        system_actor = self.get_object()
        handler = getattr(system_actor, "{}_outbox".format(request.method.lower()))
        try:
            handler(request.data, actor=request.actor)
        except NotImplementedError:
            return response.Response(status=405)
        return response.Response({}, status=200)


class WellKnownViewSet(viewsets.GenericViewSet):
    authentication_classes = []
    permission_classes = []
    renderer_classes = [renderers.JSONRenderer, renderers.WebfingerRenderer]

    @list_route(methods=["get"])
    def nodeinfo(self, request, *args, **kwargs):
        if not preferences.get("instance__nodeinfo_enabled"):
            return HttpResponse(status=404)
        data = {
            "links": [
                {
                    "rel": "http://nodeinfo.diaspora.software/ns/schema/2.0",
                    "href": utils.full_url(reverse("api:v1:instance:nodeinfo-2.0")),
                }
            ]
        }
        return response.Response(data)

    @list_route(methods=["get"])
    def webfinger(self, request, *args, **kwargs):
        if not preferences.get("federation__enabled"):
            return HttpResponse(status=405)
        try:
            resource_type, resource = webfinger.clean_resource(request.GET["resource"])
            cleaner = getattr(webfinger, "clean_{}".format(resource_type))
            result = cleaner(resource)
            handler = getattr(self, "handler_{}".format(resource_type))
            data = handler(result)
        except forms.ValidationError as e:
            return response.Response({"errors": {"resource": e.message}}, status=400)
        except KeyError:
            return response.Response(
                {"errors": {"resource": "This field is required"}}, status=400
            )

        return response.Response(data)

    def handler_acct(self, clean_result):
        username, hostname = clean_result

        if username in actors.SYSTEM_ACTORS:
            actor = actors.SYSTEM_ACTORS[username].get_actor_instance()
        else:
            try:
                actor = models.Actor.objects.local().get(preferred_username=username)
            except models.Actor.DoesNotExist:
                raise forms.ValidationError("Invalid username")

        return serializers.ActorWebfingerSerializer(actor).data


def has_library_access(request, library):
    if library.privacy_level == "everyone":
        return True
    if request.user.is_authenticated and request.user.is_superuser:
        return True

    try:
        actor = request.actor
    except AttributeError:
        return False

    return library.received_follows.filter(actor=actor, approved=True).exists()


class MusicLibraryViewSet(
    FederationMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    authentication_classes = [authentication.SignatureAuthentication]
    permission_classes = []
    renderer_classes = [renderers.ActivityPubRenderer]
    serializer_class = serializers.PaginatedCollectionSerializer
    queryset = music_models.Library.objects.all().select_related("actor")
    lookup_field = "uuid"

    def retrieve(self, request, *args, **kwargs):
        lb = self.get_object()

        conf = {
            "id": lb.get_federation_id(),
            "actor": lb.actor,
            "name": lb.name,
            "summary": lb.description,
            "items": lb.files.order_by("-creation_date"),
            "item_serializer": serializers.AudioSerializer,
        }
        page = request.GET.get("page")
        if page is None:
            serializer = serializers.LibrarySerializer(lb)
            data = serializer.data
        else:
            # if actor is requesting a specific page, we ensure library is public
            # or readable by the actor
            if not has_library_access(request, lb):
                raise exceptions.AuthenticationFailed(
                    "You do not have access to this library"
                )
            try:
                page_number = int(page)
            except Exception:
                return response.Response({"page": ["Invalid page number"]}, status=400)
            conf["page_size"] = preferences.get("federation__collection_page_size")
            p = paginator.Paginator(conf["items"], conf["page_size"])
            try:
                page = p.page(page_number)
                conf["page"] = page
                serializer = serializers.CollectionPageSerializer(conf)
                data = serializer.data
            except paginator.EmptyPage:
                return response.Response(status=404)

        return response.Response(data)
