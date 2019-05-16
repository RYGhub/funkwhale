from django.contrib.admin import register as initial_register, site, ModelAdmin  # noqa
from django.db.models.fields.related import RelatedField

from . import models
from . import tasks


def register(model):
    """
    To make the admin more performant, we ensure all the the relations
    are listed under raw_id_fields
    """

    def decorator(modeladmin):
        raw_id_fields = []
        for field in model._meta.fields:
            if isinstance(field, RelatedField):
                raw_id_fields.append(field.name)
        setattr(modeladmin, "raw_id_fields", raw_id_fields)
        return initial_register(model)(modeladmin)

    return decorator


def apply(modeladmin, request, queryset):
    queryset.update(is_approved=True)
    for id in queryset.values_list("id", flat=True):
        tasks.apply_mutation.delay(mutation_id=id)


apply.short_description = "Approve and apply"


@register(models.Mutation)
class MutationAdmin(ModelAdmin):
    list_display = [
        "uuid",
        "type",
        "created_by",
        "creation_date",
        "applied_date",
        "is_approved",
        "is_applied",
    ]
    search_fields = ["created_by__preferred_username"]
    list_filter = ["type", "is_approved", "is_applied"]
    actions = [apply]
