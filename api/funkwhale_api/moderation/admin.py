from funkwhale_api.common import admin

from . import models


@admin.register(models.InstancePolicy)
class InstancePolicyAdmin(admin.ModelAdmin):
    list_display = [
        "actor",
        "target_domain",
        "target_actor",
        "creation_date",
        "block_all",
        "reject_media",
        "silence_activity",
        "silence_notifications",
    ]
    list_filter = [
        "block_all",
        "reject_media",
        "silence_activity",
        "silence_notifications",
    ]
    search_fields = [
        "actor__fid",
        "target_domain__name",
        "target_domain__actor__fid",
        "summary",
    ]
    list_select_related = True


@admin.register(models.UserFilter)
class UserFilterAdmin(admin.ModelAdmin):
    list_display = ["uuid", "user", "target_artist", "creation_date"]
    search_fields = ["target_artist__name", "user__username", "user__email"]
    list_select_related = True
