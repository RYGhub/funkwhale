import requests

from django.conf import settings

from funkwhale_api.common import session

from . import actors
from . import serializers
from . import signing
from . import webfinger


def scan_from_account_name(account_name):
    """
    Given an account name such as library@test.library, will:

    1. Perform the webfinger lookup
    2. Perform the actor lookup
    3. Perform the library's collection lookup

    and return corresponding data in a dictionary.
    """

    data = {}
    try:
        data['webfinger'] = webfinger.get_resource(
            'acct:{}'.format(account_name))
    except requests.ConnectionError:
        return {
            'webfinger': {
                'errors': ['This webfinger resource is not reachable']
            }
        }
    except requests.HTTPError as e:
        return {
            'webfinger': {
                'errors': [
                    'Error {} during webfinger request'.format(
                        e.response.status_code)]
            }
        }

    try:
        data['actor'] = actors.get_actor_data(data['webfinger']['actor_url'])
    except requests.ConnectionError:
        data['actor'] = {
            'errors': ['This actor is not reachable']
        }
        return data
    except requests.HTTPError as e:
        data['actor'] = {
            'errors': [
                'Error {} during actor request'.format(
                    e.response.status_code)]
        }
        return data

    serializer = serializers.LibraryActorSerializer(data=data['actor'])
    serializer.is_valid(raise_exception=True)
    data['library'] = get_library_data(
        serializer.validated_data['library_url'])

    return data


def get_library_data(library_url):
    actor = actors.SYSTEM_ACTORS['library'].get_actor_instance()
    auth = signing.get_auth(actor.private_key, actor.private_key_id)
    try:
        response = session.get_session().get(
            library_url,
            auth=auth,
            timeout=5,
            verify=settings.EXTERNAL_REQUESTS_VERIFY_SSL,
            headers={
                'Content-Type': 'application/activity+json'
            }
        )
    except requests.ConnectionError:
        return {
            'errors': ['This library is not reachable']
        }
    scode = response.status_code
    if scode == 401:
        return {
            'errors': ['This library requires authentication']
        }
    elif scode == 403:
        return {
            'errors': ['Permission denied while scanning library']
        }
    elif scode >= 400:
        return {
            'errors': ['Error {} while fetching the library'.format(scode)]
        }
    serializer = serializers.PaginatedCollectionSerializer(
        data=response.json(),
    )
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data
