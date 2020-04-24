from funkwhale_api.common import admin

from . import models


@admin.register(models.Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = [
        "uuid",
        "artist",
        "attributed_to",
        "actor",
        "library",
        "creation_date",
    ]
