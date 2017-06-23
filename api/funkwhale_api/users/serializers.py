from rest_framework import serializers

from . import models


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
