import django_filters

from funkwhale_api.common import fields
from funkwhale_api.common import filters as common_filters
from funkwhale_api.moderation import filters as moderation_filters

from . import models


def filter_tags(queryset, name, value):
    non_empty_tags = [v.lower() for v in value if v]
    for tag in non_empty_tags:
        queryset = queryset.filter(artist__tagged_items__tag__name=tag).distinct()
    return queryset


TAG_FILTER = common_filters.MultipleQueryFilter(method=filter_tags)


class ChannelFilter(moderation_filters.HiddenContentFilterSet):
    q = fields.SearchFilter(
        search_fields=["artist__name", "actor__summary", "actor__preferred_username"]
    )
    tag = TAG_FILTER
    scope = common_filters.ActorScopeFilter(actor_field="attributed_to", distinct=True)

    class Meta:
        model = models.Channel
        fields = ["q", "scope", "tag"]
        hidden_content_fields_mapping = moderation_filters.USER_FILTER_CONFIG["CHANNEL"]


class IncludeChannelsFilterSet(django_filters.FilterSet):
    """

    A filterset that include a "include_channels" param. Meant for compatibility
    with clients that don't support channels yet:

    - include_channels=false : exclude objects associated with a channel
    - include_channels=true : don't exclude objects associated with a channel
    - not specified: include_channels=false

    Usage:

    class MyFilterSet(IncludeChannelsFilterSet):
        class Meta:
            include_channels_field = "album__artist__channel"

    """

    include_channels = django_filters.BooleanFilter(
        field_name="_", method="filter_include_channels"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = self.data.copy()
        self.data.setdefault("include_channels", False)

    def filter_include_channels(self, queryset, name, value):
        if value is True:
            return queryset
        else:
            params = {self.__class__.Meta.include_channels_field: None}
            return queryset.filter(**params)
