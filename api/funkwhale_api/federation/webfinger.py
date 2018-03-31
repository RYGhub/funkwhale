from django import forms
from django.conf import settings
from django.urls import reverse

from . import actors
from . import utils

VALID_RESOURCE_TYPES = ['acct']


def clean_resource(resource_string):
    if not resource_string:
        raise forms.ValidationError('Invalid resource string')

    try:
        resource_type, resource = resource_string.split(':', 1)
    except ValueError:
        raise forms.ValidationError('Missing webfinger resource type')

    if resource_type not in VALID_RESOURCE_TYPES:
        raise forms.ValidationError('Invalid webfinger resource type')

    return resource_type, resource


def clean_acct(acct_string):
    try:
        username, hostname = acct_string.split('@')
    except ValueError:
        raise forms.ValidationError('Invalid format')

    if hostname != settings.FEDERATION_HOSTNAME:
        raise forms.ValidationError('Invalid hostname')

    if username not in actors.SYSTEM_ACTORS:
        raise forms.ValidationError('Invalid username')

    return username, hostname
