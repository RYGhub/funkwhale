from django.urls import reverse
from django.conf import settings

from . import utils


def repr_instance_actor():
    """
    We do not use a serializer here, since it's pretty static
    """
    return {
        '@context': [
            'https://www.w3.org/ns/activitystreams',
            'https://w3id.org/security/v1',
            {},
        ],
        'id': utils.full_url(reverse('federation:instance-actor')),
        'type': 'Service',
        'inbox': utils.full_url(reverse('federation:instance-inbox')),
        'outbox': utils.full_url(reverse('federation:instance-outbox')),
    }
