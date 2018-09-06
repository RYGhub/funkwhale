import django_filters

from funkwhale_api.common import fields

from . import models


class FollowFilter(django_filters.FilterSet):
    pending = django_filters.CharFilter(method="filter_pending")
    ordering = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ("creation_date", "creation_date"),
            ("modification_date", "modification_date"),
        )
    )
    q = fields.SearchFilter(
        search_fields=["actor__domain", "actor__preferred_username"]
    )

    class Meta:
        model = models.Follow
        fields = ["approved", "pending", "q"]

    def filter_pending(self, queryset, field_name, value):
        if value.lower() in ["true", "1", "yes"]:
            queryset = queryset.filter(approved__isnull=True)
        return queryset


class LibraryFollowFilter(django_filters.FilterSet):
    class Meta:
        model = models.LibraryFollow
        fields = ["approved"]
