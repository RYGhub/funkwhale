from django_filters import rest_framework as filters

from funkwhale_api.common import fields
from funkwhale_api.common import search
from funkwhale_api.moderation import filters as moderation_filters

from . import models
from . import utils


class ArtistFilter(moderation_filters.HiddenContentFilterSet):
    q = fields.SearchFilter(search_fields=["name"])
    playable = filters.BooleanFilter(field_name="_", method="filter_playable")

    class Meta:
        model = models.Artist
        fields = {
            "name": ["exact", "iexact", "startswith", "icontains"],
            "playable": "exact",
        }
        hidden_content_fields_mapping = moderation_filters.USER_FILTER_CONFIG["ARTIST"]

    def filter_playable(self, queryset, name, value):
        actor = utils.get_actor_from_request(self.request)
        return queryset.playable_by(actor, value)


class TrackFilter(moderation_filters.HiddenContentFilterSet):
    q = fields.SearchFilter(search_fields=["title", "album__title", "artist__name"])
    playable = filters.BooleanFilter(field_name="_", method="filter_playable")

    class Meta:
        model = models.Track
        fields = {
            "title": ["exact", "iexact", "startswith", "icontains"],
            "playable": ["exact"],
            "artist": ["exact"],
            "album": ["exact"],
            "license": ["exact"],
        }
        hidden_content_fields_mapping = moderation_filters.USER_FILTER_CONFIG["TRACK"]

    def filter_playable(self, queryset, name, value):
        actor = utils.get_actor_from_request(self.request)
        return queryset.playable_by(actor, value)


class UploadFilter(filters.FilterSet):
    library = filters.CharFilter("library__uuid")
    track = filters.UUIDFilter("track__uuid")
    track_artist = filters.UUIDFilter("track__artist__uuid")
    album_artist = filters.UUIDFilter("track__album__artist__uuid")
    library = filters.UUIDFilter("library__uuid")
    playable = filters.BooleanFilter(field_name="_", method="filter_playable")
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
        ]

    def filter_playable(self, queryset, name, value):
        actor = utils.get_actor_from_request(self.request)
        return queryset.playable_by(actor, value)


class AlbumFilter(moderation_filters.HiddenContentFilterSet):
    playable = filters.BooleanFilter(field_name="_", method="filter_playable")
    q = fields.SearchFilter(search_fields=["title", "artist__name"])

    class Meta:
        model = models.Album
        fields = ["playable", "q", "artist"]
        hidden_content_fields_mapping = moderation_filters.USER_FILTER_CONFIG["ALBUM"]

    def filter_playable(self, queryset, name, value):
        actor = utils.get_actor_from_request(self.request)
        return queryset.playable_by(actor, value)
