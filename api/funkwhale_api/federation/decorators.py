from django.db import transaction

from rest_framework import decorators
from rest_framework import permissions
from rest_framework import response
from rest_framework import status

from funkwhale_api.common import utils as common_utils

from . import api_serializers
from . import filters
from . import models
from . import tasks
from . import utils


def fetches_route():
    @transaction.atomic
    def fetches(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.method == "GET":
            queryset = models.Fetch.objects.get_for_object(obj).select_related("actor")
            queryset = queryset.order_by("-creation_date")
            filterset = filters.FetchFilter(request.GET, queryset=queryset)
            page = self.paginate_queryset(filterset.qs)
            if page is not None:
                serializer = api_serializers.FetchSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = api_serializers.FetchSerializer(queryset, many=True)
            return response.Response(serializer.data)
        if request.method == "POST":
            if utils.is_local(obj.fid):
                return response.Response(
                    {"detail": "Cannot fetch a local object"}, status=400
                )

            fetch = models.Fetch.objects.create(
                url=obj.fid, actor=request.user.actor, object=obj
            )
            common_utils.on_commit(tasks.fetch.delay, fetch_id=fetch.pk)
            serializer = api_serializers.FetchSerializer(fetch)
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)

    return decorators.action(
        methods=["get", "post"],
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
    )(fetches)
