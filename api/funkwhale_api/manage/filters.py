from django import forms
from django_filters import rest_framework as filters

from funkwhale_api.common import fields
from funkwhale_api.common import search

from funkwhale_api.federation import models as federation_models
from funkwhale_api.federation import utils as federation_utils
from funkwhale_api.moderation import models as moderation_models
from funkwhale_api.music import models as music_models
from funkwhale_api.users import models as users_models


class ManageUploadFilterSet(filters.FilterSet):
    q = fields.SearchFilter(
        search_fields=[
            "track__title",
            "track__album__title",
            "track__artist__name",
            "source",
        ]
    )

    class Meta:
        model = music_models.Upload
        fields = ["q", "track__album", "track__artist", "track"]


class ManageArtistFilterSet(filters.FilterSet):
    q = fields.SmartSearchFilter(
        config=search.SearchConfig(
            search_fields={
                "name": {"to": "name"},
                "fid": {"to": "fid"},
                "mbid": {"to": "mbid"},
            },
            filter_fields={
                "domain": {
                    "handler": lambda v: federation_utils.get_domain_query_from_url(v)
                }
            },
        )
    )

    class Meta:
        model = music_models.Artist
        fields = ["q", "name", "mbid", "fid"]


class ManageAlbumFilterSet(filters.FilterSet):
    q = fields.SmartSearchFilter(
        config=search.SearchConfig(
            search_fields={
                "title": {"to": "title"},
                "fid": {"to": "fid"},
                "artist": {"to": "artist__name"},
                "mbid": {"to": "mbid"},
            },
            filter_fields={
                "artist_id": {"to": "artist_id", "field": forms.IntegerField()},
                "domain": {
                    "handler": lambda v: federation_utils.get_domain_query_from_url(v)
                },
            },
        )
    )

    class Meta:
        model = music_models.Album
        fields = ["q", "title", "mbid", "fid", "artist"]


class ManageTrackFilterSet(filters.FilterSet):
    q = fields.SmartSearchFilter(
        config=search.SearchConfig(
            search_fields={
                "title": {"to": "title"},
                "fid": {"to": "fid"},
                "mbid": {"to": "mbid"},
                "artist": {"to": "artist__name"},
                "album": {"to": "album__title"},
                "album_artist": {"to": "album__artist__name"},
                "copyright": {"to": "copyright"},
            },
            filter_fields={
                "album_id": {"to": "album_id", "field": forms.IntegerField()},
                "album_artist_id": {
                    "to": "album__artist_id",
                    "field": forms.IntegerField(),
                },
                "artist_id": {"to": "artist_id", "field": forms.IntegerField()},
                "license": {"to": "license"},
                "domain": {
                    "handler": lambda v: federation_utils.get_domain_query_from_url(v)
                },
            },
        )
    )

    class Meta:
        model = music_models.Track
        fields = ["q", "title", "mbid", "fid", "artist", "album", "license"]


class ManageDomainFilterSet(filters.FilterSet):
    q = fields.SearchFilter(search_fields=["name"])

    class Meta:
        model = federation_models.Domain
        fields = ["name"]


class ManageActorFilterSet(filters.FilterSet):
    q = fields.SmartSearchFilter(
        config=search.SearchConfig(
            search_fields={
                "name": {"to": "name"},
                "username": {"to": "preferred_username"},
                "email": {"to": "user__email"},
                "bio": {"to": "summary"},
                "type": {"to": "type"},
            },
            filter_fields={
                "domain": {"to": "domain__name__iexact"},
                "username": {"to": "preferred_username__iexact"},
                "email": {"to": "user__email__iexact"},
            },
        )
    )
    local = filters.BooleanFilter(field_name="_", method="filter_local")

    class Meta:
        model = federation_models.Actor
        fields = ["q", "domain", "type", "manually_approves_followers", "local"]

    def filter_local(self, queryset, name, value):
        return queryset.local(value)


class ManageUserFilterSet(filters.FilterSet):
    q = fields.SmartSearchFilter(
        config=search.SearchConfig(
            search_fields={
                "name": {"to": "name"},
                "username": {"to": "username"},
                "email": {"to": "email"},
            }
        )
    )

    class Meta:
        model = users_models.User
        fields = [
            "q",
            "is_active",
            "privacy_level",
            "is_staff",
            "is_superuser",
            "permission_library",
            "permission_settings",
            "permission_moderation",
        ]


class ManageInvitationFilterSet(filters.FilterSet):
    q = fields.SearchFilter(search_fields=["owner__username", "code", "owner__email"])
    is_open = filters.BooleanFilter(method="filter_is_open")

    class Meta:
        model = users_models.Invitation
        fields = ["q", "is_open"]

    def filter_is_open(self, queryset, field_name, value):
        if value is None:
            return queryset
        return queryset.open(value)


class ManageInstancePolicyFilterSet(filters.FilterSet):
    q = fields.SearchFilter(
        search_fields=[
            "summary",
            "target_domain__name",
            "target_actor__username",
            "target_actor__domain__name",
        ]
    )

    class Meta:
        model = moderation_models.InstancePolicy
        fields = [
            "q",
            "block_all",
            "silence_activity",
            "silence_notifications",
            "reject_media",
        ]
