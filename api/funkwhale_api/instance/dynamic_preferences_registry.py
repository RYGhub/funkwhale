from django.forms import widgets
from django.core.validators import FileExtensionValidator

from dynamic_preferences import types
from dynamic_preferences.registries import global_preferences_registry

raven = types.Section("raven")
instance = types.Section("instance")
ui = types.Section("ui")


@global_preferences_registry.register
class InstanceName(types.StringPreference):
    show_in_api = True
    section = instance
    name = "name"
    default = ""
    verbose_name = "Public name"
    help_text = "The public name of your instance, displayed in the about page."
    field_kwargs = {"required": False}


@global_preferences_registry.register
class InstanceShortDescription(types.StringPreference):
    show_in_api = True
    section = instance
    name = "short_description"
    default = ""
    verbose_name = "Short description"
    help_text = "Instance succinct description, displayed in the about page."
    field_kwargs = {"required": False}


@global_preferences_registry.register
class InstanceLongDescription(types.StringPreference):
    show_in_api = True
    section = instance
    name = "long_description"
    verbose_name = "Long description"
    default = ""
    help_text = (
        "Instance long description, displayed in the about page (markdown allowed)."
    )
    widget = widgets.Textarea
    field_kwargs = {"required": False}


@global_preferences_registry.register
class InstanceTerms(types.StringPreference):
    show_in_api = True
    section = instance
    name = "terms"
    verbose_name = "Terms of service"
    default = ""
    help_text = (
        "Terms of service and privacy policy for your instance (markdown allowed)."
    )
    widget = widgets.Textarea
    field_kwargs = {"required": False}


@global_preferences_registry.register
class InstanceRules(types.StringPreference):
    show_in_api = True
    section = instance
    name = "rules"
    verbose_name = "Rules"
    default = ""
    help_text = "Rules/Code of Conduct (markdown allowed)."
    widget = widgets.Textarea
    field_kwargs = {"required": False}


@global_preferences_registry.register
class InstanceContactEmail(types.StringPreference):
    show_in_api = True
    section = instance
    name = "contact_email"
    verbose_name = "Contact email"
    default = ""
    help_text = "A contact email for visitors who need to contact an admin or moderator"
    field_kwargs = {"required": False}


@global_preferences_registry.register
class InstanceSupportMessage(types.StringPreference):
    show_in_api = True
    section = instance
    name = "support_message"
    verbose_name = "Support message"
    default = ""
    help_text = (
        "A short message that will be displayed periodically to local users. "
        "Use it to ask for financial support or anything else you might need. "
        "(markdown allowed)."
    )
    widget = widgets.Textarea
    field_kwargs = {"required": False}


@global_preferences_registry.register
class InstanceFunkwhaleSupportMessageEnabled(types.BooleanPreference):
    show_in_api = True
    section = instance
    name = "funkwhale_support_message_enabled"
    verbose_name = "Funkwhale Support message"
    default = True
    help_text = (
        "If this is enabled, we will periodically display a message to encourage "
        "local users to support Funkwhale."
    )


@global_preferences_registry.register
class RavenDSN(types.StringPreference):
    show_in_api = True
    section = raven
    name = "front_dsn"
    default = "https://9e0562d46b09442bb8f6844e50cbca2b@sentry.eliotberriot.com/4"
    verbose_name = "Raven DSN key (front-end)"

    help_text = (
        "A Raven DSN key used to report front-ent errors to "
        "a sentry instance. Keeping the default one will report errors to "
        "Funkwhale developers."
    )
    field_kwargs = {"required": False}


@global_preferences_registry.register
class InstanceNodeinfoPrivate(types.BooleanPreference):
    show_in_api = False
    section = instance
    name = "nodeinfo_private"
    default = False
    verbose_name = "Private mode in nodeinfo"
    help_text = (
        "Indicate in the nodeinfo endpoint that you do not want your instance "
        "to be tracked by third-party services. "
        "There is no guarantee these tools will honor this setting though."
    )


@global_preferences_registry.register
class InstanceNodeinfoStatsEnabled(types.BooleanPreference):
    show_in_api = False
    section = instance
    name = "nodeinfo_stats_enabled"
    default = True
    verbose_name = "Enable usage and library stats in nodeinfo endpoint"
    help_text = (
        "Disable this if you don't want to share usage and library statistics "
        "in the nodeinfo endpoint but don't want to disable it completely."
    )


@global_preferences_registry.register
class CustomCSS(types.StringPreference):
    show_in_api = True
    section = ui
    name = "custom_css"
    verbose_name = "Custom CSS code"
    default = ""
    help_text = (
        "Custom CSS code, to be included in a <style> tag on all pages. "
        "Loading third-party resources such as fonts or images can affect the performance "
        "of the app and the privacy of your users."
    )
    widget = widgets.Textarea
    field_kwargs = {"required": False}


class ImageWidget(widgets.ClearableFileInput):
    pass


class ImagePreference(types.FilePreference):
    widget = ImageWidget
    field_kwargs = {
        "validators": [
            FileExtensionValidator(allowed_extensions=["png", "jpg", "jpeg", "webp"])
        ]
    }


@global_preferences_registry.register
class Banner(ImagePreference):
    show_in_api = True
    section = instance
    name = "banner"
    verbose_name = "Banner image"
    default = None
    help_text = "This banner will be displayed on your pod's landing and about page. At least 600x100px recommended."
    field_kwargs = {"required": False}
