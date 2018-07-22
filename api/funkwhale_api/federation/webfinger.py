from django import forms
from django.conf import settings

from funkwhale_api.common import session

from . import serializers

VALID_RESOURCE_TYPES = ["acct"]


def clean_resource(resource_string):
    if not resource_string:
        raise forms.ValidationError("Invalid resource string")

    try:
        resource_type, resource = resource_string.split(":", 1)
    except ValueError:
        raise forms.ValidationError("Missing webfinger resource type")

    if resource_type not in VALID_RESOURCE_TYPES:
        raise forms.ValidationError("Invalid webfinger resource type")

    return resource_type, resource


def clean_acct(acct_string, ensure_local=True):
    try:
        username, hostname = acct_string.split("@")
    except ValueError:
        raise forms.ValidationError("Invalid format")

    if ensure_local and hostname.lower() != settings.FEDERATION_HOSTNAME:
        raise forms.ValidationError("Invalid hostname {}".format(hostname))

    return username, hostname


def get_resource(resource_string):
    resource_type, resource = clean_resource(resource_string)
    username, hostname = clean_acct(resource, ensure_local=False)
    url = "https://{}/.well-known/webfinger?resource={}".format(
        hostname, resource_string
    )
    response = session.get_session().get(
        url, verify=settings.EXTERNAL_REQUESTS_VERIFY_SSL, timeout=5
    )
    response.raise_for_status()
    serializer = serializers.ActorWebfingerSerializer(data=response.json())
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data
