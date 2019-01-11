from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from funkwhale_api.common.permissions import ConditionalAuthentication

from .client import api


class ReleaseDetail(APIView):
    permission_classes = [ConditionalAuthentication]

    def get(self, request, *args, **kwargs):
        result = api.releases.get(id=kwargs["uuid"], includes=["artists", "recordings"])
        return Response(result)


class ArtistDetail(APIView):
    permission_classes = [ConditionalAuthentication]

    def get(self, request, *args, **kwargs):
        result = api.artists.get(id=kwargs["uuid"], includes=["release-groups"])
        # import json; print(json.dumps(result, indent=4))
        return Response(result)


class ReleaseGroupBrowse(APIView):
    permission_classes = [ConditionalAuthentication]

    def get(self, request, *args, **kwargs):
        result = api.release_groups.browse(artist=kwargs["artist_uuid"])
        return Response(result)


class ReleaseBrowse(APIView):
    permission_classes = [ConditionalAuthentication]

    def get(self, request, *args, **kwargs):
        result = api.releases.browse(
            release_group=kwargs["release_group_uuid"],
            includes=["recordings", "artist-credits"],
        )
        return Response(result)


class SearchViewSet(viewsets.ViewSet):
    permission_classes = [ConditionalAuthentication]

    @action(methods=["get"], detail=False)
    def recordings(self, request, *args, **kwargs):
        query = request.GET["query"]
        results = api.recordings.search(query)
        return Response(results)

    @action(methods=["get"], detail=False)
    def releases(self, request, *args, **kwargs):
        query = request.GET["query"]
        results = api.releases.search(query)
        return Response(results)

    @action(methods=["get"], detail=False)
    def artists(self, request, *args, **kwargs):
        query = request.GET["query"]
        results = api.artists.search(query)
        # results = musicbrainzngs.search_artists(query)
        return Response(results)
