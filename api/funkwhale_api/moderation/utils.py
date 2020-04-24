from rest_framework import serializers

from funkwhale_api.federation import models as federation_models

from . import models
from . import serializers as moderation_serializers


NOTE_TARGET_FIELDS = {
    "report": {
        "queryset": models.Report.objects.all(),
        "id_attr": "uuid",
        "id_field": serializers.UUIDField(),
    },
    "request": {
        "queryset": models.UserRequest.objects.all(),
        "id_attr": "uuid",
        "id_field": serializers.UUIDField(),
    },
    "account": {
        "queryset": federation_models.Actor.objects.all(),
        "id_attr": "full_username",
        "id_field": serializers.EmailField(),
        "get_query": moderation_serializers.get_actor_query,
    },
}


def get_signup_form_additional_fields_serializer(customization):
    fields = (customization or {}).get("fields", []) or []

    class AdditionalFieldsSerializer(serializers.Serializer):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field in fields:
                required = bool(field.get("required", True))
                self.fields[field["label"]] = serializers.CharField(
                    max_length=5000,
                    required=required,
                    allow_null=not required,
                    allow_blank=not required,
                )

    return AdditionalFieldsSerializer(required=fields, allow_null=not fields)
