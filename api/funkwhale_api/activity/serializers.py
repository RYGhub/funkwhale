from rest_framework import serializers

from funkwhale_api.activity import record


class ModelSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="get_activity_url")
    local_id = serializers.IntegerField(source="id")
    # url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return self.get_id(obj)


class AutoSerializer(serializers.Serializer):
    """
    A serializer that will automatically use registered activity serializers
    to serialize an henerogeneous list of objects (favorites, listenings, etc.)
    """

    def to_representation(self, instance):
        serializer = record.registry[instance._meta.label]["serializer"](instance)
        return serializer.data
