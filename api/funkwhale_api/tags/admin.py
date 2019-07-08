from funkwhale_api.common import admin

from . import models


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "creation_date"]
    search_fields = ["name"]
    list_select_related = True


@admin.register(models.TaggedItem)
class TaggedItemAdmin(admin.ModelAdmin):
    list_display = ["object_id", "content_type", "tag", "creation_date"]
    search_fields = ["tag__name"]
    list_filter = ["content_type"]
    list_select_related = True
