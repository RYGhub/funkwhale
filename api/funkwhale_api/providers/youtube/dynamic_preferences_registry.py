from django import forms
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import Section, StringPreference

youtube = Section("providers_youtube")


@global_preferences_registry.register
class APIKey(StringPreference):
    section = youtube
    name = "api_key"
    default = "CHANGEME"
    verbose_name = "YouTube API key"
    help_text = "The API key used to query YouTube. Get one at https://console.developers.google.com/."
    widget = forms.PasswordInput
    field_kwargs = {"required": False}
