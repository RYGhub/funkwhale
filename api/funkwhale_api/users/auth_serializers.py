from django.contrib import auth

from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, validated_data):
        user = auth.authenticate(request=None, **validated_data)
        if user is None:
            raise serializers.ValidationError("Invalid username or password")

        validated_data["user"] = user
        return validated_data
