from django.db.models import Count

from django_filters import rest_framework as filters

from funkwhale_api.common import fields
from funkwhale_api.music import models as music_models


class ManageTrackFileFilterSet(filters.FilterSet):
    q = fields.SearchFilter(search_fields=[
        'track__title',
        'track__album__title',
        'track__artist__name',
        'source',
    ])

    class Meta:
        model = music_models.TrackFile
        fields = [
            'q',
            'track__album',
            'track__artist',
            'track',
            'library_track'
        ]
