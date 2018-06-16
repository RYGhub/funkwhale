import django_filters

from funkwhale_api.common import fields

from . import models


class ImportRequestFilter(django_filters.FilterSet):

    q = fields.SearchFilter(
        search_fields=["artist_name", "user__username", "albums", "comment"]
    )

    class Meta:
        model = models.ImportRequest
        fields = {
            "artist_name": ["exact", "iexact", "startswith", "icontains"],
            "status": ["exact"],
            "user__username": ["exact"],
        }
