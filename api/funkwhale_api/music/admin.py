from funkwhale_api.common import admin

from . import models


@admin.register(models.Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ["name", "mbid", "creation_date"]
    search_fields = ["name", "mbid"]


@admin.register(models.Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ["title", "artist", "mbid", "release_date", "creation_date"]
    search_fields = ["title", "artist__name", "mbid"]
    list_select_related = True


@admin.register(models.Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ["title", "artist", "album", "mbid"]
    search_fields = ["title", "artist__name", "album__title", "mbid"]
    list_select_related = ["album__artist", "artist"]


@admin.register(models.ImportBatch)
class ImportBatchAdmin(admin.ModelAdmin):
    list_display = ["submitted_by", "creation_date", "import_request", "status"]
    list_select_related = ["submitted_by", "import_request"]
    list_filter = ["status"]
    search_fields = ["import_request__name", "source", "batch__pk", "mbid"]


@admin.register(models.ImportJob)
class ImportJobAdmin(admin.ModelAdmin):
    list_display = ["source", "batch", "upload", "status", "mbid"]
    list_select_related = ["upload", "batch"]
    search_fields = ["source", "batch__pk", "mbid"]
    list_filter = ["status"]


@admin.register(models.Upload)
class UploadAdmin(admin.ModelAdmin):
    list_display = [
        "track",
        "audio_file",
        "source",
        "duration",
        "mimetype",
        "size",
        "bitrate",
        "import_status",
    ]
    list_select_related = ["track"]
    search_fields = [
        "source",
        "acoustid_track_id",
        "track__title",
        "track__album__title",
        "track__artist__name",
    ]
    list_filter = ["mimetype", "import_status", "library__privacy_level"]


@admin.register(models.UploadVersion)
class UploadVersionAdmin(admin.ModelAdmin):
    list_display = [
        "upload",
        "audio_file",
        "mimetype",
        "size",
        "bitrate",
        "creation_date",
        "accessed_date",
    ]
    list_select_related = ["upload"]
    search_fields = [
        "upload__source",
        "upload__acoustid_track_id",
        "upload__track__title",
        "upload__track__album__title",
        "upload__track__artist__name",
    ]
    list_filter = ["mimetype"]


def launch_scan(modeladmin, request, queryset):
    for library in queryset:
        library.schedule_scan(actor=request.user.actor, force=True)


launch_scan.short_description = "Launch scan"


@admin.register(models.Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "actor", "uuid", "privacy_level", "creation_date"]
    list_select_related = True
    search_fields = ["actor__username", "name", "description"]
    list_filter = ["privacy_level"]
    actions = [launch_scan]


@admin.register(models.LibraryScan)
class LibraryScanAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "library",
        "actor",
        "status",
        "creation_date",
        "modification_date",
        "status",
        "total_files",
        "processed_files",
        "errored_files",
    ]
    list_select_related = True
    search_fields = ["actor__username", "library__name"]
    list_filter = ["status"]
