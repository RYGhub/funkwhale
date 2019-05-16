import django.dispatch

mutation_created = django.dispatch.Signal(providing_args=["mutation"])
mutation_updated = django.dispatch.Signal(
    providing_args=["mutation", "old_is_approved", "new_is_approved"]
)
