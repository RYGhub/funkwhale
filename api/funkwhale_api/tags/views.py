from django.db.models import functions
from rest_framework import viewsets

import django_filters.rest_framework

from funkwhale_api.users.oauth import permissions as oauth_permissions

from . import filters
from . import models
from . import serializers


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "name"
    queryset = (
        models.Tag.objects.all()
        .annotate(__size=functions.Length("name"))
        .order_by("name")
    )
    serializer_class = serializers.TagSerializer
    permission_classes = [oauth_permissions.ScopePermission]
    required_scope = "libraries"
    anonymous_policy = "setting"
    filterset_class = filters.TagFilter
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
