from dynamic_preferences import types
from dynamic_preferences.registries import global_preferences_registry

from rest_framework import serializers

from funkwhale_api.common import preferences as common_preferences
from funkwhale_api.common import serializers as common_serializers
from funkwhale_api.common import utils as common_utils

from . import models

moderation = types.Section("moderation")


@global_preferences_registry.register
class AllowListEnabled(types.BooleanPreference):
    section = moderation
    name = "allow_list_enabled"
    verbose_name = "Enable allow-listing"
    help_text = "If enabled, only interactions with explicitely allowed domains will be authorized."
    default = False


@global_preferences_registry.register
class AllowListPublic(types.BooleanPreference):
    section = moderation
    name = "allow_list_public"
    verbose_name = "Publish your allowed-domains list"
    help_text = (
        "If enabled, everyone will be able to retrieve the list of domains you allowed. "
        "This is useful on open setups, to help people decide if they want to join your pod, or to "
        "make your moderation policy public."
    )
    default = False


@global_preferences_registry.register
class UnauthenticatedReportTypes(common_preferences.StringListPreference):
    show_in_api = True
    section = moderation
    name = "unauthenticated_report_types"
    default = ["takedown_request", "illegal_content"]
    verbose_name = "Accountless report categories"
    help_text = "A list of categories for which external users (without an account) can submit a report"
    choices = models.REPORT_TYPES
    field_kwargs = {"choices": choices, "required": False}


@global_preferences_registry.register
class SignupApprovalEnabled(types.BooleanPreference):
    show_in_api = True
    section = moderation
    name = "signup_approval_enabled"
    verbose_name = "Enable manual sign-up validation"
    help_text = "If enabled, new registrations will go to a moderation queue and need to be reviewed by moderators."
    default = False


CUSTOM_FIELDS_TYPES = [
    "short_text",
    "long_text",
]


class CustomFieldSerializer(serializers.Serializer):
    label = serializers.CharField()
    required = serializers.BooleanField(default=True)
    input_type = serializers.ChoiceField(choices=CUSTOM_FIELDS_TYPES)


class CustomFormSerializer(serializers.Serializer):
    help_text = common_serializers.ContentSerializer(required=False, allow_null=True)
    fields = serializers.ListField(
        child=CustomFieldSerializer(), min_length=0, max_length=10, required=False
    )

    def validate_help_text(self, v):
        if not v:
            return
        v["html"] = common_utils.render_html(
            v["text"], content_type=v["content_type"], permissive=True
        )
        return v


@global_preferences_registry.register
class SignupFormCustomization(common_preferences.SerializedPreference):
    show_in_api = True
    section = moderation
    name = "signup_form_customization"
    verbose_name = "Sign-up form customization"
    help_text = "Configure custom fields and help text for your sign-up form"
    required = False
    default = {}
    data_serializer_class = CustomFormSerializer
