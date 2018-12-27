from django_filters import rest_framework as filters

from funkwhale_api.common import fields
from funkwhale_api.federation import models as federation_models
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


class ManageDomainFilterSet(filters.FilterSet):
    q = fields.SearchFilter(search_fields=["name"])

    class Meta:
        model = federation_models.Domain
        fields = ["name"]


class ManageUserFilterSet(filters.FilterSet):
    q = fields.SearchFilter(search_fields=["username", "email", "name"])

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
