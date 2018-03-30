from django.urls import reverse
from django.conf import settings

from dynamic_preferences.registries import global_preferences_registry

from . import utils


def repr_instance_actor():
    """
    We do not use a serializer here, since it's pretty static
    """
    actor_url = utils.full_url(reverse('federation:instance-actor'))
    preferences = global_preferences_registry.manager()
    public_key = preferences['federation__public_key']

    return {
        '@context': [
            'https://www.w3.org/ns/activitystreams',
            'https://w3id.org/security/v1',
            {},
        ],
        'id': utils.full_url(reverse('federation:instance-actor')),
        'type': 'Person',
        'inbox': utils.full_url(reverse('federation:instance-inbox')),
        'outbox': utils.full_url(reverse('federation:instance-outbox')),
        'preferredUsername': 'service',
        'name': 'Service Bot - {}'.format(settings.FEDERATION_HOSTNAME),
        'summary': 'Bot account for federating with {}'.format(
            settings.FEDERATION_HOSTNAME
        ),
        'publicKey': {
            'id': '{}#main-key'.format(actor_url),
            'owner': actor_url,
            'publicKeyPem': public_key
        },

    }
