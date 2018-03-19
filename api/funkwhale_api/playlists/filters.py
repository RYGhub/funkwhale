from django_filters import rest_framework as filters

from . import models



class PlaylistFilter(filters.FilterSet):

    class Meta:
        model = models.Playlist
        fields = {
            'user': ['exact'],
        }
