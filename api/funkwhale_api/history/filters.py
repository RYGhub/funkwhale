from funkwhale_api.moderation import filters as moderation_filters

from . import models


class ListeningFilter(moderation_filters.HiddenContentFilterSet):
    class Meta:
        model = models.Listening
        hidden_content_fields_mapping = moderation_filters.USER_FILTER_CONFIG[
            "LISTENING"
        ]
        fields = ["hidden"]
