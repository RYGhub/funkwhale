from django.urls import reverse

from funkwhale_api.federation import actors
from funkwhale_api.federation import utils


def test_actor_fetching(r_mock):
    payload = {
        'id': 'https://actor.mock/users/actor#main-key',
        'owner': 'test',
        'publicKeyPem': 'test_pem',
    }
    actor_url = 'https://actor.mock/'
    r_mock.get(actor_url, json=payload)
    r = actors.get_actor_data(actor_url)

    assert r == payload


def test_get_library(settings, preferences):
    preferences['federation__public_key'] = 'public_key'
    expected = {
        'preferred_username': 'library',
        'domain': settings.FEDERATION_HOSTNAME,
        'type': 'Person',
        'name': '{}\'s library'.format(settings.FEDERATION_HOSTNAME),
        'manually_approves_followers': True,
        'url': utils.full_url(
            reverse(
                'federation:instance-actors-detail',
                kwargs={'actor': 'library'})),
        'shared_inbox_url': utils.full_url(
            reverse(
                'federation:instance-actors-inbox',
                kwargs={'actor': 'library'})),
        'inbox_url': utils.full_url(
            reverse(
                'federation:instance-actors-inbox',
                kwargs={'actor': 'library'})),
        'public_key': 'public_key',
        'summary': 'Bot account to federate with {}\'s library'.format(
        settings.FEDERATION_HOSTNAME),
    }
    actor = actors.SYSTEM_ACTORS['library']['get_actor']()
    for key, value in expected.items():
        assert getattr(actor, key) == value
