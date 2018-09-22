import django.dispatch

upload_import_status_updated = django.dispatch.Signal(
    providing_args=["old_status", "new_status", "upload"]
)
