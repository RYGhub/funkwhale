import django_filters

from . import models


class ArtistFilter(django_filters.FilterSet):

    class Meta:
        model = models.Artist
        fields = {
            'name': ['exact', 'iexact', 'startswith']
        }
