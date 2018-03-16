from django.contrib import admin

from . import models


@admin.register(models.Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'privacy_level', 'creation_date']
    search_fields = ['name', ]
    list_select_related = True


@admin.register(models.PlaylistTrack)
class PlaylistTrackAdmin(admin.ModelAdmin):
    list_display = ['playlist', 'track', 'position', ]
    search_fields = ['track__name', 'playlist__name']
    list_select_related = True
