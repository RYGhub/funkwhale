from django import forms
from django.core import paginator
from django.db import transaction
from django.http import HttpResponse, Http404
from django.urls import reverse
from rest_framework import mixins, response, viewsets
from rest_framework.decorators import detail_route, list_route

from funkwhale_api.common import preferences
from funkwhale_api.music import models as music_models
from funkwhale_api.users.permissions import HasUserPermission

from . import (
    actors,
    authentication,
    filters,
    library,
    models,
    permissions,
    renderers,
    serializers,
    tasks,
    utils,
    webfinger,
)


class FederationMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not preferences.get("federation__enabled"):
            return HttpResponse(status=405)
        return super().dispatch(request, *args, **kwargs)


class ActorViewSet(FederationMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    lookup_field = "user__username"
    authentication_classes = [authentication.SignatureAuthentication]
    permission_classes = []
    renderer_classes = [renderers.ActivityPubRenderer]
    queryset = models.Actor.objects.local().select_related("user")
    serializer_class = serializers.ActorSerializer

    @detail_route(methods=["get", "post"])
    def inbox(self, request, *args, **kwargs):
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
                actor = models.Actor.objects.local().get(user__username=username)
            except models.Actor.DoesNotExist:
                raise forms.ValidationError("Invalid username")

        return serializers.ActorWebfingerSerializer(actor).data


class MusicFilesViewSet(FederationMixin, viewsets.GenericViewSet):
    authentication_classes = [authentication.SignatureAuthentication]
    permission_classes = [permissions.LibraryFollower]
    renderer_classes = [renderers.ActivityPubRenderer]

    def list(self, request, *args, **kwargs):
        page = request.GET.get("page")
        library = actors.SYSTEM_ACTORS["library"].get_actor_instance()
        qs = (
            music_models.TrackFile.objects.order_by("-creation_date")
            .select_related("track__artist", "track__album__artist")
            .filter(library_track__isnull=True)
        )
        if page is None:
            conf = {
                "id": utils.full_url(reverse("federation:music:files-list")),
                "page_size": preferences.get("federation__collection_page_size"),
                "items": qs,
                "item_serializer": serializers.AudioSerializer,
                "actor": library,
            }
            serializer = serializers.PaginatedCollectionSerializer(conf)
            data = serializer.data
        else:
            try:
                page_number = int(page)
            except Exception:
                return response.Response({"page": ["Invalid page number"]}, status=400)
            p = paginator.Paginator(
                qs, preferences.get("federation__collection_page_size")
            )
            try:
                page = p.page(page_number)
                conf = {
                    "id": utils.full_url(reverse("federation:music:files-list")),
                    "page": page,
                    "item_serializer": serializers.AudioSerializer,
                    "actor": library,
                }
                serializer = serializers.CollectionPageSerializer(conf)
                data = serializer.data
            except paginator.EmptyPage:
                return response.Response(status=404)

        return response.Response(data)


class LibraryViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (HasUserPermission,)
    required_permissions = ["federation"]
    queryset = models.Library.objects.all().select_related("actor", "follow")
    lookup_field = "uuid"
    filter_class = filters.LibraryFilter
    serializer_class = serializers.APILibrarySerializer
    ordering_fields = (
        "id",
        "creation_date",
        "fetched_date",
        "actor__domain",
        "tracks_count",
    )

    @list_route(methods=["get"])
    def fetch(self, request, *args, **kwargs):
        account = request.GET.get("account")
        if not account:
            return response.Response({"account": "This field is mandatory"}, status=400)

        data = library.scan_from_account_name(account)
        return response.Response(data)

    @detail_route(methods=["post"])
    def scan(self, request, *args, **kwargs):
        library = self.get_object()
        serializer = serializers.APILibraryScanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = tasks.scan_library.delay(
            library_id=library.pk, until=serializer.validated_data.get("until")
        )
        return response.Response({"task": result.id})

    @list_route(methods=["get"])
    def following(self, request, *args, **kwargs):
        library_actor = actors.SYSTEM_ACTORS["library"].get_actor_instance()
        queryset = (
            models.Follow.objects.filter(actor=library_actor)
            .select_related("actor", "target")
            .order_by("-creation_date")
        )
        filterset = filters.FollowFilter(request.GET, queryset=queryset)
        final_qs = filterset.qs
        serializer = serializers.APIFollowSerializer(final_qs, many=True)
        data = {"results": serializer.data, "count": len(final_qs)}
        return response.Response(data)

    @list_route(methods=["get", "patch"])
    def followers(self, request, *args, **kwargs):
        if request.method.lower() == "patch":
            serializer = serializers.APILibraryFollowUpdateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            follow = serializer.save()
            return response.Response(serializers.APIFollowSerializer(follow).data)

        library_actor = actors.SYSTEM_ACTORS["library"].get_actor_instance()
        queryset = (
            models.Follow.objects.filter(target=library_actor)
            .select_related("actor", "target")
            .order_by("-creation_date")
        )
        filterset = filters.FollowFilter(request.GET, queryset=queryset)
        final_qs = filterset.qs
        serializer = serializers.APIFollowSerializer(final_qs, many=True)
        data = {"results": serializer.data, "count": len(final_qs)}
        return response.Response(data)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = serializers.APILibraryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status=201)


class LibraryTrackViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (HasUserPermission,)
    required_permissions = ["federation"]
    queryset = (
        models.LibraryTrack.objects.all()
        .select_related("library__actor", "library__follow", "local_track_file")
        .prefetch_related("import_jobs")
    )
    filter_class = filters.LibraryTrackFilter
    serializer_class = serializers.APILibraryTrackSerializer
    ordering_fields = (
        "id",
        "artist_name",
        "title",
        "album_title",
        "creation_date",
        "modification_date",
        "fetched_date",
        "published_date",
    )

    @list_route(methods=["post"])
    def action(self, request, *args, **kwargs):
        queryset = models.LibraryTrack.objects.filter(local_track_file__isnull=True)
        serializer = serializers.LibraryTrackActionSerializer(
            request.data, queryset=queryset, context={"submitted_by": request.user}
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return response.Response(result, status=200)
