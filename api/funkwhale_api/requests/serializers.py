from rest_framework import serializers

from funkwhale_api.users.serializers import UserBasicSerializer

from . import models


class ImportRequestSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)

    class Meta:
        model = models.ImportRequest
        fields = (
            "id",
            "status",
            "albums",
            "artist_name",
            "user",
            "creation_date",
            "imported_date",
            "comment",
        )
        read_only_fields = ("creation_date", "imported_date", "user", "status")

    def create(self, validated_data):
        validated_data["user"] = self.context["user"]
        return super().create(validated_data)
