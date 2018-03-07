from django.db.models import Count

from django_filters import rest_framework as filters

from . import models


class ListenableMixin(filters.FilterSet):
    listenable = filters.BooleanFilter(name='_', method='filter_listenable')

    def filter_listenable(self, queryset, name, value):
        queryset = queryset.annotate(
            files_count=Count('tracks__files')
        )
        if value:
            return queryset.filter(files_count__gt=0)
        else:
            return queryset.filter(files_count=0)


class ArtistFilter(ListenableMixin):

    class Meta:
        model = models.Artist
        fields = {
            'name': ['exact', 'iexact', 'startswith', 'icontains'],
            'listenable': 'exact',
        }


class AlbumFilter(ListenableMixin):
    listenable = filters.BooleanFilter(name='_', method='filter_listenable')

    class Meta:
        model = models.Album
        fields = ['listenable']
