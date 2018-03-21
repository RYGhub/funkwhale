from django_filters import rest_framework as filters

from funkwhale_api.music import utils

from . import models



class PlaylistFilter(filters.FilterSet):
    q = filters.CharFilter(name='_', method='filter_q')

    class Meta:
        model = models.Playlist
        fields = {
            'user': ['exact'],
            'name': ['exact', 'icontains'],
            'q': 'exact',
        }

    def filter_q(self, queryset, name, value):
        query = utils.get_query(value, ['name', 'user__username'])
        return queryset.filter(query)
