from django.db.models import Q

from django_filters import rest_framework as filters


USER_FILTER_CONFIG = {
    "ARTIST": {"target_artist": ["pk"]},
    "ALBUM": {"target_artist": ["artist__pk"]},
    "TRACK": {"target_artist": ["artist__pk", "album__artist__pk"]},
    "LISTENING": {"target_artist": ["track__album__artist__pk", "track__artist__pk"]},
    "TRACK_FAVORITE": {
        "target_artist": ["track__album__artist__pk", "track__artist__pk"]
    },
}


def get_filtered_content_query(config, user):
    final_query = None
    for filter_field, model_fields in config.items():
        query = None
        ids = user.content_filters.values_list(filter_field, flat=True)
        for model_field in model_fields:
            q = Q(**{"{}__in".format(model_field): ids})
            if query:
                query |= q
            else:
                query = q

        final_query = query
    return final_query


class HiddenContentFilterSet(filters.FilterSet):
    """
    A filterset that include a "hidden" param:
    - hidden=true : list user hidden/filtered objects
    - hidden=false : list all objects user hidden/filtered objects
    - not specified: hidden=false

    Usage:

    class MyFilterSet(HiddenContentFilterSet):
        class Meta:
            hidden_content_fields_mapping = {'target_artist': ['pk']}

    Will map UserContentFilter.artist values to the pk field of the filtered model.

    """

    hidden = filters.BooleanFilter(field_name="_", method="filter_hidden_content")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = self.data.copy()
        self.data.setdefault("hidden", False)

    def filter_hidden_content(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated:
            # no filter to apply
            return queryset

        config = self.__class__.Meta.hidden_content_fields_mapping
        final_query = get_filtered_content_query(config, user)

        if value is True:
            return queryset.filter(final_query)
        else:
            return queryset.exclude(final_query)
