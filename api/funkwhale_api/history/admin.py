from django.contrib import admin

from . import models

@admin.register(models.Listening)
class ListeningAdmin(admin.ModelAdmin):
    list_display = ['track', 'end_date', 'user', 'session_key']
    search_fields = ['track__name', 'user__username']
