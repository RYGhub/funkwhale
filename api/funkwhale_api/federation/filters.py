import django_filters

from . import models


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
