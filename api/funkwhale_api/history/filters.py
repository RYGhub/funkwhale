import django_filters

from funkwhale_api.moderation import filters as moderation_filters

from . import models


class ListeningFilter(moderation_filters.HiddenContentFilterSet):
    username = django_filters.CharFilter("user__username")
    domain = django_filters.CharFilter("user__actor__domain_id")

    class Meta:
        model = models.Listening
        hidden_content_fields_mapping = moderation_filters.USER_FILTER_CONFIG[
            "LISTENING"
        ]
        fields = ["hidden"]
