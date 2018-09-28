import requests
from django.conf import settings

from funkwhale_api.common import session

from . import serializers, signing


def get_library_data(library_url, actor):
    auth = signing.get_auth(actor.private_key, actor.private_key_id)
    try:
        response = session.get_session().get(
            library_url,
            auth=auth,
            timeout=5,
            verify=settings.EXTERNAL_REQUESTS_VERIFY_SSL,
            headers={"Content-Type": "application/activity+json"},
        )
    except requests.ConnectionError:
        return {"errors": ["This library is not reachable"]}
    scode = response.status_code
    if scode == 401:
        return {"errors": ["This library requires authentication"]}
    elif scode == 403:
        return {"errors": ["Permission denied while scanning library"]}
    elif scode >= 400:
        return {"errors": ["Error {} while fetching the library".format(scode)]}
    serializer = serializers.LibrarySerializer(data=response.json())
    if not serializer.is_valid():
        return {"errors": ["Invalid ActivityPub response from remote library"]}

    return serializer.validated_data


def get_library_page(library, page_url, actor):
    auth = signing.get_auth(actor.private_key, actor.private_key_id)
    response = session.get_session().get(
        page_url,
        auth=auth,
        timeout=5,
        verify=settings.EXTERNAL_REQUESTS_VERIFY_SSL,
        headers={"Content-Type": "application/activity+json"},
    )
    serializer = serializers.CollectionPageSerializer(
        data=response.json(),
        context={"library": library, "item_serializer": serializers.UploadSerializer},
    )
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data
