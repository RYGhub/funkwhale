from django.contrib import admin

from . import models


@admin.register(models.ImportRequest)
class ImportRequestAdmin(admin.ModelAdmin):
    list_display = ["artist_name", "user", "status", "creation_date"]
    list_select_related = ["user"]
    list_filter = ["status"]
    search_fields = ["artist_name", "comment", "albums"]
