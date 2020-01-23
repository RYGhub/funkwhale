import re

from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

from rest_auth.serializers import PasswordResetSerializer as PRS
from rest_auth.registration.serializers import RegisterSerializer as RS, get_adapter
from rest_framework import serializers

from funkwhale_api.activity import serializers as activity_serializers
from funkwhale_api.common import models as common_models
from funkwhale_api.common import serializers as common_serializers
from funkwhale_api.common import utils as common_utils
from funkwhale_api.federation import models as federation_models
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
NOOP = object()


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

    def validate(self, validated_data):
        data = super().validate(validated_data)
        # we create a fake user obj with validated data so we can validate
        # password properly (we have a password validator that requires
        # a user object)
        user = models.User(username=data["username"], email=data["email"])
        get_adapter().clean_password(data["password1"], user)
        return data

    def validate_username(self, value):
        username = super().validate_username(value)
        duplicates = federation_models.Actor.objects.local().filter(
            preferred_username__iexact=username
        )
        if duplicates.exists():
            raise serializers.ValidationError(
                "A user with that username already exists."
            )
        return username

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


class UserBasicSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = models.User
        fields = ["id", "username", "name", "date_joined", "avatar"]

    def get_avatar(self, o):
        return common_serializers.AttachmentSerializer(
            o.actor.attachment_icon if o.actor else None
        ).data


class UserWriteSerializer(serializers.ModelSerializer):
    summary = common_serializers.ContentSerializer(required=False, allow_null=True)
    avatar = common_serializers.RelatedField(
        "uuid",
        queryset=common_models.Attachment.objects.all().local().attached(False),
        serializer=None,
        queryset_filter=lambda qs, context: qs.filter(
            actor=context["request"].user.actor
        ),
        write_only=True,
    )

    class Meta:
        model = models.User
        fields = [
            "name",
            "privacy_level",
            "avatar",
            "instance_support_message_display_date",
            "funkwhale_support_message_display_date",
            "summary",
        ]

    def update(self, obj, validated_data):
        if not obj.actor:
            obj.create_actor()
        summary = validated_data.pop("summary", NOOP)
        avatar = validated_data.pop("avatar", NOOP)

        obj = super().update(obj, validated_data)

        if summary != NOOP:
            common_utils.attach_content(obj.actor, "summary_obj", summary)
        if avatar != NOOP:
            obj.actor.attachment_icon = avatar
            obj.actor.save(update_fields=["attachment_icon"])
        return obj

    def to_representation(self, obj):
        repr = super().to_representation(obj)
        repr["avatar"] = common_serializers.AttachmentSerializer(
            obj.actor.attachment_icon
        ).data
        return repr


class UserReadSerializer(serializers.ModelSerializer):

    permissions = serializers.SerializerMethodField()
    full_username = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

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

    def get_avatar(self, o):
        return common_serializers.AttachmentSerializer(o.actor.attachment_icon).data

    def get_permissions(self, o):
        return o.get_permissions()

    def get_full_username(self, o):
        if o.actor:
            return o.actor.full_username


class MeSerializer(UserReadSerializer):
    quota_status = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()

    class Meta(UserReadSerializer.Meta):
        fields = UserReadSerializer.Meta.fields + [
            "quota_status",
            "instance_support_message_display_date",
            "funkwhale_support_message_display_date",
            "summary",
        ]

    def get_quota_status(self, o):
        return o.get_quota_status() if o.actor else 0

    def get_summary(self, o):
        if not o.actor or not o.actor.summary_obj:
            return
        return common_serializers.ContentSerializer(o.actor.summary_obj).data


class PasswordResetSerializer(PRS):
    def get_email_options(self):
        return {"extra_email_context": adapters.get_email_context()}


class UserDeleteSerializer(serializers.Serializer):
    password = serializers.CharField()
    confirm = serializers.BooleanField()

    def validate_password(self, value):
        if not self.instance.check_password(value):
            raise serializers.ValidationError("Invalid password")

    def validate_confirm(self, value):
        if not value:
            raise serializers.ValidationError("Please confirm deletion")
        return value
