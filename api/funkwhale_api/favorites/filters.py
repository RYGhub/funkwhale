from django_filters import rest_framework as filters

from funkwhale_api.common import fields

from . import models


class TrackFavoriteFilter(filters.FilterSet):
    q = fields.SearchFilter(
        search_fields=["track__title", "track__artist__name", "track__album__title"]
    )

    class Meta:
        model = models.TrackFavorite
        fields = ["user", "q"]
