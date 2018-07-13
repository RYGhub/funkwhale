from django.conf import settings
from rest_auth.serializers import PasswordResetSerializer as PRS
from rest_auth.registration.serializers import RegisterSerializer as RS
from rest_framework import serializers

from versatileimagefield.serializers import VersatileImageFieldSerializer

from funkwhale_api.activity import serializers as activity_serializers

from . import models


class RegisterSerializer(RS):
    invitation = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )

    def validate_invitation(self, value):
        if not value:
            return

        try:
            return models.Invitation.objects.open().get(code__iexact=value)
        except models.Invitation.DoesNotExist:
            raise serializers.ValidationError("Invalid invitation code")

    def save(self, request):
        user = super().save(request)
        if self.validated_data.get("invitation"):
            user.invitation = self.validated_data.get("invitation")
            user.save(update_fields=["invitation"])
        return user


class UserActivitySerializer(activity_serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    name = serializers.CharField(source="username")
    local_id = serializers.CharField(source="username")

    class Meta:
        model = models.User
        fields = ["id", "local_id", "name", "type"]

    def get_type(self, obj):
        return "Person"


class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ["id", "username", "name", "date_joined"]


avatar_field = VersatileImageFieldSerializer(
    allow_null=True,
    sizes=[
        ("original", "url"),
        ("square_crop", "crop__400x400"),
        ("medium_square_crop", "crop__200x200"),
        ("small_square_crop", "crop__50x50"),
    ],
)


class UserWriteSerializer(serializers.ModelSerializer):
    avatar = avatar_field

    class Meta:
        model = models.User
        fields = ["name", "privacy_level", "avatar"]


class UserReadSerializer(serializers.ModelSerializer):

    permissions = serializers.SerializerMethodField()
    avatar = avatar_field

    class Meta:
        model = models.User
        fields = [
            "id",
            "username",
            "name",
            "email",
            "is_staff",
            "is_superuser",
            "permissions",
            "date_joined",
            "privacy_level",
            "avatar",
        ]

    def get_permissions(self, o):
        return o.get_permissions()


class PasswordResetSerializer(PRS):
    def get_email_options(self):
        return {"extra_email_context": {"funkwhale_url": settings.FUNKWHALE_URL}}
