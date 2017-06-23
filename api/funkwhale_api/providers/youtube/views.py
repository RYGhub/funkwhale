from rest_framework.views import APIView
from rest_framework.response import Response
from funkwhale_api.common.permissions import ConditionalAuthentication

from .client import client


class APISearch(APIView):
    permission_classes = [ConditionalAuthentication]

    def get(self, request, *args, **kwargs):
        results = client.search(request.GET['query'])
        return Response(results)


class APISearchs(APIView):
    permission_classes = [ConditionalAuthentication]

    def post(self, request, *args, **kwargs):
        results = client.search_multiple(request.data)
        return Response(results)
