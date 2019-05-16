import re

from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

from rest_auth.serializers import PasswordResetSerializer as PRS
from rest_auth.registration.serializers import RegisterSerializer as RS
from rest_framework import serializers
from versatileimagefield.serializers import VersatileImageFieldSerializer

from funkwhale_api.activity import serializers as activity_serializers
from funkwhale_api.common import serializers as common_serializers
from . import adapters
from . import models


@deconstructible
class ASCIIUsernameValidator(validators.RegexValidator):
    regex = r"^[\w]+$"
    message = _(
        "Enter a valid username. This value may contain only English letters, "
        "numbers, and _ characters."
    )
    flags = re.ASCII


username_validators = [ASCIIUsernameValidator()]


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
        user.actor = models.create_actor(user)
        user.save(update_fields=["actor"])

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


class AvatarField(
    common_serializers.StripExifImageField, VersatileImageFieldSerializer
):
    pass


avatar_field = AvatarField(allow_null=True, sizes="square")


class UserBasicSerializer(serializers.ModelSerializer):
    avatar = avatar_field

    class Meta:
        model = models.User
        fields = ["id", "username", "name", "date_joined", "avatar"]


class UserWriteSerializer(serializers.ModelSerializer):
    avatar = avatar_field

    class Meta:
        model = models.User
        fields = ["name", "privacy_level", "avatar"]


class UserReadSerializer(serializers.ModelSerializer):

    permissions = serializers.SerializerMethodField()
    full_username = serializers.SerializerMethodField()
    avatar = avatar_field

    class Meta:
        model = models.User
        fields = [
            "id",
            "username",
            "full_username",
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

    def get_full_username(self, o):
        if o.actor:
            return o.actor.full_username


class MeSerializer(UserReadSerializer):
    quota_status = serializers.SerializerMethodField()

    class Meta(UserReadSerializer.Meta):
        fields = UserReadSerializer.Meta.fields + ["quota_status"]

    def get_quota_status(self, o):
        return o.get_quota_status() if o.actor else 0


class PasswordResetSerializer(PRS):
    def get_email_options(self):
        return {"extra_email_context": adapters.get_email_context()}
