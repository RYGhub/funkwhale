from funkwhale_api.common import admin

from . import models


@admin.register(models.Radio)
class RadioAdmin(admin.ModelAdmin):
    list_display = ["user", "name", "is_public", "creation_date", "config"]
    list_select_related = ["user"]
    list_filter = ["is_public"]
    search_fields = ["name", "description"]


@admin.register(models.RadioSession)
class RadioSessionAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "custom_radio",
        "radio_type",
        "creation_date",
        "related_object",
    ]

    list_select_related = ["user", "custom_radio"]
    list_filter = ["radio_type"]


@admin.register(models.RadioSessionTrack)
class RadioSessionTrackAdmin(admin.ModelAdmin):
    list_display = ["id", "session", "position", "track"]

    list_select_related = ["track", "session"]
