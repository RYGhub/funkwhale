from rest_framework import serializers

from funkwhale_api.activity import serializers as activity_serializers

from . import models


class UserActivitySerializer(activity_serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    name = serializers.CharField(source='username')

    class Meta:
        model = models.User
        fields = [
            'id',
            'name',
            'type'
        ]

    def get_type(self, obj):
        return 'Person'


class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ['id', 'username', 'name', 'date_joined']


class UserSerializer(serializers.ModelSerializer):

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
        ]

    def get_permissions(self, o):
        perms = {}
        for internal_codename, conf in o.relevant_permissions.items():
            perms[conf['external_codename']] = {
                'status': o.has_perm(internal_codename)
            }
        return perms
