from rest_framework import serializers


class ModelSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='get_activity_url')
    # url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return self.get_id(obj)
