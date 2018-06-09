import django_filters

from . import models


class RadioFilter(django_filters.FilterSet):
    class Meta:
        model = models.Radio
        fields = {"name": ["exact", "iexact", "startswith", "icontains"]}
