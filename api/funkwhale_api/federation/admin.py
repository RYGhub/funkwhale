from django.contrib import admin

from . import models


@admin.register(models.Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = [
        'url',
        'domain',
        'preferred_username',
        'type',
        'creation_date',
        'last_fetch_date']
    search_fields = ['url', 'domain', 'preferred_username']
    list_filter = [
        'type'
    ]


@admin.register(models.Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = [
        'actor',
        'target',
        'approved',
        'creation_date'
    ]
    list_filter = [
        'approved'
    ]
    search_fields = ['actor__url', 'target__url']
    list_select_related = True


@admin.register(models.Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display = [
        'actor',
        'url',
        'creation_date',
        'fetched_date',
        'tracks_count']
    search_fields = ['actor__url', 'url']
    list_filter = [
        'federation_enabled',
        'download_files',
        'autoimport',
    ]
    list_select_related = True


@admin.register(models.LibraryTrack)
class LibraryTrackAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'artist_name',
        'album_title',
        'url',
        'library',
        'creation_date',
        'published_date',
    ]
    search_fields = [
        'library__url', 'url', 'artist_name', 'title', 'album_title']
    list_select_related = True
