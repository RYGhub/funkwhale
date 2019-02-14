from rest_framework import serializers

from funkwhale_api.music import models as music_models
from . import models


class FilteredArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = music_models.Artist
        fields = ["id", "name"]


class TargetSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["artist"])
    id = serializers.CharField()

    def to_representation(self, value):
        if value["type"] == "artist":
            data = FilteredArtistSerializer(value["obj"]).data
            data.update({"type": "artist"})
            return data

    def to_internal_value(self, value):
        if value["type"] == "artist":
            field = serializers.PrimaryKeyRelatedField(
                queryset=music_models.Artist.objects.all()
            )
        value["obj"] = field.to_internal_value(value["id"])
        return value


class UserFilterSerializer(serializers.ModelSerializer):
    target = TargetSerializer()

    class Meta:
        model = models.UserFilter
        fields = ["uuid", "target", "creation_date"]
        read_only_fields = ["uuid", "creation_date"]

    def validate(self, data):
        target = data.pop("target")
        if target["type"] == "artist":
            data["target_artist"] = target["obj"]

        return data
