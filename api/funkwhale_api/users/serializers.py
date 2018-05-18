from django.conf import settings

from rest_framework import serializers
from rest_auth.serializers import PasswordResetSerializer as PRS
from funkwhale_api.activity import serializers as activity_serializers

from . import models


class UserActivitySerializer(activity_serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    name = serializers.CharField(source='username')
    local_id = serializers.CharField(source='username')

    class Meta:
        model = models.User
        fields = [
            'id',
            'local_id',
            'name',
            'type'
        ]

    def get_type(self, obj):
        return 'Person'


class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ['id', 'username', 'name', 'date_joined']


class UserWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = [
            'name',
            'privacy_level'
        ]


class UserReadSerializer(serializers.ModelSerializer):

    permissions = serializers.SerializerMethodField()

    class Meta:
        model = models.User
        fields = [
            'id',
            'username',
            'name',
            'email',
            'is_staff',
            'is_superuser',
            'permissions',
            'date_joined',
            'privacy_level',
        ]

    def get_permissions(self, o):
        return o.get_permissions()


class PasswordResetSerializer(PRS):
    def get_email_options(self):
        return {
            'extra_email_context': {
                'funkwhale_url': settings.FUNKWHALE_URL
            }
        }
