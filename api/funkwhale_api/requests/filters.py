import django_filters

from . import models


class ImportRequestFilter(django_filters.FilterSet):

    class Meta:
        model = models.ImportRequest
        fields = {
            'artist_name': ['exact', 'iexact', 'startswith', 'icontains'],
            'status': ['exact'],
            'user__username': ['exact'],
        }
