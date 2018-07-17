from django.db.models import Count
from django_filters import rest_framework as filters

from funkwhale_api.music import utils

from . import models


class PlaylistFilter(filters.FilterSet):
    q = filters.CharFilter(name="_", method="filter_q")
    listenable = filters.BooleanFilter(name="_", method="filter_listenable")

    class Meta:
        model = models.Playlist
        fields = {
            "user": ["exact"],
            "name": ["exact", "icontains"],
            "q": "exact",
            "listenable": "exact",
        }

    def filter_listenable(self, queryset, name, value):
        queryset = queryset.annotate(plts_count=Count("playlist_tracks"))
        if value:
            return queryset.filter(plts_count__gt=0)
        else:
            return queryset.filter(plts_count=0)

    def filter_q(self, queryset, name, value):
        query = utils.get_query(value, ["name", "user__username"])
        return queryset.filter(query)
