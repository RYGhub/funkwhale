from django.db.models import Count

from django_filters import rest_framework as filters

from funkwhale_api.common import fields
from . import models


class ListenableMixin(filters.FilterSet):
    listenable = filters.BooleanFilter(name="_", method="filter_listenable")

    def filter_listenable(self, queryset, name, value):
        queryset = queryset.annotate(files_count=Count("tracks__files"))
        if value:
            return queryset.filter(files_count__gt=0)
        else:
            return queryset.filter(files_count=0)


class ArtistFilter(ListenableMixin):
    q = fields.SearchFilter(search_fields=["name"])

    class Meta:
        model = models.Artist
        fields = {
            "name": ["exact", "iexact", "startswith", "icontains"],
            "listenable": "exact",
        }


class TrackFilter(filters.FilterSet):
    q = fields.SearchFilter(search_fields=["title", "album__title", "artist__name"])
    listenable = filters.BooleanFilter(name="_", method="filter_listenable")

    class Meta:
        model = models.Track
        fields = {
            "title": ["exact", "iexact", "startswith", "icontains"],
            "listenable": ["exact"],
            "artist": ["exact"],
            "album": ["exact"],
        }

    def filter_listenable(self, queryset, name, value):
        queryset = queryset.annotate(files_count=Count("files"))
        if value:
            return queryset.filter(files_count__gt=0)
        else:
            return queryset.filter(files_count=0)


class ImportBatchFilter(filters.FilterSet):
    q = fields.SearchFilter(search_fields=["submitted_by__username", "source"])

    class Meta:
        model = models.ImportBatch
        fields = {"status": ["exact"], "source": ["exact"], "submitted_by": ["exact"]}


class ImportJobFilter(filters.FilterSet):
    q = fields.SearchFilter(search_fields=["batch__submitted_by__username", "source"])

    class Meta:
        model = models.ImportJob
        fields = {
            "batch": ["exact"],
            "batch__status": ["exact"],
            "batch__source": ["exact"],
            "batch__submitted_by": ["exact"],
            "status": ["exact"],
            "source": ["exact"],
        }


class AlbumFilter(ListenableMixin):
    listenable = filters.BooleanFilter(name="_", method="filter_listenable")
    q = fields.SearchFilter(search_fields=["title", "artist__name" "source"])

    class Meta:
        model = models.Album
        fields = ["listenable", "q", "artist"]
