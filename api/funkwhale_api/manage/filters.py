from django import forms
from django.db.models import Q
from django.conf import settings

import django_filters
from django_filters import rest_framework as filters

from funkwhale_api.common import fields
from funkwhale_api.common import search

from funkwhale_api.federation import models as federation_models
from funkwhale_api.federation import utils as federation_utils
from funkwhale_api.moderation import models as moderation_models
from funkwhale_api.music import models as music_models
from funkwhale_api.users import models as users_models


class ActorField(forms.CharField):
    def clean(self, value):
        value = super().clean(value)
        if not value:
            return value

        parts = value.split("@")

        return {
            "username": parts[0],
            "domain": parts[1] if len(parts) > 1 else settings.FEDERATION_HOSTNAME,
        }


def get_actor_filter(actor_field):
    def handler(v):
        if not v:
            return Q(**{actor_field: None})
        return Q(
            **{
                "{}__preferred_username__iexact".format(actor_field): v["username"],
                "{}__domain__name__iexact".format(actor_field): v["domain"],
            }
        )

    return {"field": ActorField(), "handler": handler}


class ManageArtistFilterSet(filters.FilterSet):
    q = fields.SmartSearchFilter(
        config=search.SearchConfig(
            search_fields={
                "name": {"to": "name"},
                "fid": {"to": "fid"},
                "mbid": {"to": "mbid"},
            },
            filter_fields={
                "uuid": {"to": "uuid"},
                "domain": {
                    "handler": lambda v: federation_utils.get_domain_query_from_url(v)
                },
                "library_id": {
                    "to": "tracks__uploads__library_id",
                    "field": forms.IntegerField(),
                    "distinct": True,
                },
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
                "uuid": {"to": "uuid"},
                "artist_id": {"to": "artist_id", "field": forms.IntegerField()},
                "domain": {
                    "handler": lambda v: federation_utils.get_domain_query_from_url(v)
                },
                "library_id": {
                    "to": "tracks__uploads__library_id",
                    "field": forms.IntegerField(),
                    "distinct": True,
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
                "uuid": {"to": "uuid"},
                "license": {"to": "license"},
                "domain": {
                    "handler": lambda v: federation_utils.get_domain_query_from_url(v)
                },
                "library_id": {
                    "to": "uploads__library_id",
                    "field": forms.IntegerField(),
                    "distinct": True,
                },
            },
        )
    )

    class Meta:
        model = music_models.Track
        fields = ["q", "title", "mbid", "fid", "artist", "album", "license"]


class ManageLibraryFilterSet(filters.FilterSet):
    ordering = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ("creation_date", "creation_date"),
            ("_uploads_count", "uploads_count"),
            ("followers_count", "followers_count"),
        )
    )
    q = fields.SmartSearchFilter(
        config=search.SearchConfig(
            search_fields={
                "name": {"to": "name"},
                "description": {"to": "description"},
                "fid": {"to": "fid"},
            },
            filter_fields={
                "uuid": {"to": "uuid"},
                "artist_id": {
                    "to": "uploads__track__artist_id",
                    "field": forms.IntegerField(),
                    "distinct": True,
                },
                "album_id": {
                    "to": "uploads__track__album_id",
                    "field": forms.IntegerField(),
                    "distinct": True,
                },
                "track_id": {
                    "to": "uploads__track__id",
                    "field": forms.IntegerField(),
                    "distinct": True,
                },
                "domain": {"to": "actor__domain_id"},
                "account": get_actor_filter("actor"),
                "privacy_level": {"to": "privacy_level"},
            },
        )
    )
    domain = filters.CharFilter("actor__domain_id")

    class Meta:
        model = music_models.Library
        fields = ["q", "name", "fid", "privacy_level", "domain"]


class ManageUploadFilterSet(filters.FilterSet):
    ordering = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ("creation_date", "creation_date"),
            ("modification_date", "modification_date"),
            ("accessed_date", "accessed_date"),
            ("size", "size"),
            ("bitrate", "bitrate"),
            ("duration", "duration"),
        )
    )
    q = fields.SmartSearchFilter(
        config=search.SearchConfig(
            search_fields={
                "source": {"to": "source"},
                "fid": {"to": "fid"},
                "track": {"to": "track__title"},
                "album": {"to": "track__album__title"},
                "artist": {"to": "track__artist__name"},
            },
            filter_fields={
                "uuid": {"to": "uuid"},
                "library_id": {"to": "library_id", "field": forms.IntegerField()},
                "artist_id": {"to": "track__artist_id", "field": forms.IntegerField()},
                "album_id": {"to": "track__album_id", "field": forms.IntegerField()},
                "track_id": {"to": "track__id", "field": forms.IntegerField()},
                "domain": {"to": "library__actor__domain_id"},
                "import_reference": {"to": "import_reference"},
                "type": {"to": "mimetype"},
                "status": {"to": "import_status"},
                "account": get_actor_filter("library__actor"),
                "privacy_level": {"to": "library__privacy_level"},
            },
        )
    )
    domain = filters.CharFilter("library__actor__domain_id")
    privacy_level = filters.CharFilter("library__privacy_level")

    class Meta:
        model = music_models.Upload
        fields = [
            "q",
            "fid",
            "privacy_level",
            "domain",
            "mimetype",
            "import_reference",
            "import_status",
        ]


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
                "uuid": {"to": "uuid"},
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
