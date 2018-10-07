from django.contrib.admin import register as initial_register, site, ModelAdmin  # noqa
from django.db.models.fields.related import RelatedField


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
