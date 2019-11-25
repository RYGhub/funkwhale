from django_filters import rest_framework as filters

from funkwhale_api.audio import filters as audio_filters
from funkwhale_api.common import fields
from funkwhale_api.common import filters as common_filters
from funkwhale_api.common import search
from funkwhale_api.moderation import filters as moderation_filters

from . import models
from . import utils


def filter_tags(queryset, name, value):
    non_empty_tags = [v.lower() for v in value if v]
    for tag in non_empty_tags:
        queryset = queryset.filter(tagged_items__tag__name=tag).distinct()
    return queryset


TAG_FILTER = common_filters.MultipleQueryFilter(method=filter_tags)


class ArtistFilter(
    audio_filters.IncludeChannelsFilterSet, moderation_filters.HiddenContentFilterSet
):
    q = fields.SearchFilter(search_fields=["name"])
    playable = filters.BooleanFilter(field_name="_", method="filter_playable")
    tag = TAG_FILTER
    scope = common_filters.ActorScopeFilter(
        actor_field="tracks__uploads__library__actor", distinct=True
    )

    class Meta:
        model = models.Artist
        fields = {
            "name": ["exact", "iexact", "startswith", "icontains"],
            "playable": ["exact"],
            "scope": ["exact"],
            "mbid": ["exact"],
        }
        hidden_content_fields_mapping = moderation_filters.USER_FILTER_CONFIG["ARTIST"]
        include_channels_field = "channel"

    def filter_playable(self, queryset, name, value):
        actor = utils.get_actor_from_request(self.request)
        return queryset.playable_by(actor, value)


class TrackFilter(
    audio_filters.IncludeChannelsFilterSet, moderation_filters.HiddenContentFilterSet
):
    q = fields.SearchFilter(search_fields=["title", "album__title", "artist__name"])
    playable = filters.BooleanFilter(field_name="_", method="filter_playable")
    tag = TAG_FILTER
    id = common_filters.MultipleQueryFilter(coerce=int)
    scope = common_filters.ActorScopeFilter(
        actor_field="uploads__library__actor", distinct=True
    )

    class Meta:
        model = models.Track
        fields = {
            "title": ["exact", "iexact", "startswith", "icontains"],
            "playable": ["exact"],
            "id": ["exact"],
            "artist": ["exact"],
            "album": ["exact"],
            "license": ["exact"],
            "scope": ["exact"],
            "mbid": ["exact"],
        }
        hidden_content_fields_mapping = moderation_filters.USER_FILTER_CONFIG["TRACK"]
        include_channels_field = "artist__channel"

    def filter_playable(self, queryset, name, value):
        actor = utils.get_actor_from_request(self.request)
        return queryset.playable_by(actor, value)


class UploadFilter(audio_filters.IncludeChannelsFilterSet):
    library = filters.CharFilter("library__uuid")
    track = filters.UUIDFilter("track__uuid")
    track_artist = filters.UUIDFilter("track__artist__uuid")
    album_artist = filters.UUIDFilter("track__album__artist__uuid")
    library = filters.UUIDFilter("library__uuid")
    playable = filters.BooleanFilter(field_name="_", method="filter_playable")
    scope = common_filters.ActorScopeFilter(actor_field="library__actor", distinct=True)
    q = fields.SmartSearchFilter(
        config=search.SearchConfig(
            search_fields={
                "track_artist": {"to": "track__artist__name"},
                "album_artist": {"to": "track__album__artist__name"},
                "album": {"to": "track__album__title"},
                "title": {"to": "track__title"},
            },
            filter_fields={
                "artist": {"to": "track__artist__name__iexact"},
                "mimetype": {"to": "mimetype"},
                "album": {"to": "track__album__title__iexact"},
                "title": {"to": "track__title__iexact"},
                "status": {"to": "import_status"},
            },
        )
    )

    class Meta:
        model = models.Upload
        fields = [
            "playable",
            "import_status",
            "mimetype",
            "track",
            "track_artist",
            "album_artist",
            "library",
            "import_reference",
            "scope",
        ]
        include_channels_field = "track__artist__channel"

    def filter_playable(self, queryset, name, value):
        actor = utils.get_actor_from_request(self.request)
        return queryset.playable_by(actor, value)


class AlbumFilter(
    audio_filters.IncludeChannelsFilterSet, moderation_filters.HiddenContentFilterSet
):
    playable = filters.BooleanFilter(field_name="_", method="filter_playable")
    q = fields.SearchFilter(search_fields=["title", "artist__name"])
    tag = TAG_FILTER
    scope = common_filters.ActorScopeFilter(
        actor_field="tracks__uploads__library__actor", distinct=True
    )

    class Meta:
        model = models.Album
        fields = ["playable", "q", "artist", "scope", "mbid"]
        hidden_content_fields_mapping = moderation_filters.USER_FILTER_CONFIG["ALBUM"]
        include_channels_field = "artist__channel"

    def filter_playable(self, queryset, name, value):
        actor = utils.get_actor_from_request(self.request)
        return queryset.playable_by(actor, value)
