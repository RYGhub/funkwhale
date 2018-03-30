from django.urls import reverse

from funkwhale_api.federation import keys
from funkwhale_api.federation import serializers


def test_repr_instance_actor(db, preferences, settings):
    _, public_key = keys.get_key_pair()
    preferences['federation__public_key'] = public_key.decode('utf-8')
    settings.FEDERATION_HOSTNAME = 'test.federation'
    settings.FUNKWHALE_URL = 'https://test.federation'
    actor_url = settings.FUNKWHALE_URL + reverse('federation:instance-actor')
    inbox_url = settings.FUNKWHALE_URL + reverse('federation:instance-inbox')
    outbox_url = settings.FUNKWHALE_URL + reverse('federation:instance-outbox')

    expected = {
        '@context': [
            'https://www.w3.org/ns/activitystreams',
            'https://w3id.org/security/v1',
            {},
        ],
        'id': actor_url,
        'type': 'Person',
        'preferredUsername': 'service',
        'name': 'Service Bot - test.federation',
        'summary': 'Bot account for federating with test.federation',
        'inbox': inbox_url,
        'outbox': outbox_url,
        'publicKey': {
            'id': '{}#main-key'.format(actor_url),
            'owner': actor_url,
            'publicKeyPem': public_key.decode('utf-8')
        },
    }

    assert expected == serializers.repr_instance_actor()
