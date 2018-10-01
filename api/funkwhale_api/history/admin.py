from funkwhale_api.common import admin

from . import models


@admin.register(models.Listening)
class ListeningAdmin(admin.ModelAdmin):
    list_display = ["track", "creation_date", "user", "session_key"]
    search_fields = ["track__name", "user__username"]
    list_select_related = ["user", "track"]
