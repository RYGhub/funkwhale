import django_filters

from . import models


class LibraryFilter(django_filters.FilterSet):
    approved = django_filters.BooleanFilter('following__approved')

    class Meta:
        model = models.Library
        fields = {
            'approved': ['exact'],
            'federation_enabled': ['exact'],
            'download_files': ['exact'],
            'autoimport': ['exact'],
            'tracks_count': ['exact'],
        }


class FollowFilter(django_filters.FilterSet):
    ordering = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('creation_date', 'creation_date'),
            ('modification_date', 'modification_date'),
        ),
    )

    class Meta:
        model = models.Follow
        fields = {
            'approved': ['exact'],
        }
