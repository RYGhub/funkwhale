import django.dispatch

track_file_import_status_updated = django.dispatch.Signal(
    providing_args=["old_status", "new_status", "track_file"]
)
