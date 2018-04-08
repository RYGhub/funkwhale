from django import forms
from django.conf import settings
from django.urls import reverse

from funkwhale_api.common import session

from . import actors
from . import utils
from . import serializers

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


def clean_acct(acct_string, ensure_local=True):
    try:
        username, hostname = acct_string.split('@')
    except ValueError:
        raise forms.ValidationError('Invalid format')

    if ensure_local and hostname.lower() != settings.FEDERATION_HOSTNAME:
        raise forms.ValidationError(
            'Invalid hostname {}'.format(hostname))

    if username not in actors.SYSTEM_ACTORS:
        raise forms.ValidationError('Invalid username')

    return username, hostname


def get_resource(resource_string):
    resource_type, resource = clean_resource(resource_string)
    username, hostname = clean_acct(resource, ensure_local=False)
    url = 'https://{}/.well-known/webfinger?resource={}'.format(
        hostname, resource_string)
    response = session.get_session().get(url)
    response.raise_for_status()
    serializer = serializers.ActorWebfingerSerializer(data=response.json())
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data
