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
    "account": {
        "queryset": federation_models.Actor.objects.all(),
        "id_attr": "full_username",
        "id_field": serializers.EmailField(),
        "get_query": moderation_serializers.get_actor_query,
    },
}
