import requests

from django.urls import reverse
from django.conf import settings

from dynamic_preferences.registries import global_preferences_registry

from . import models
from . import utils


def get_actor_data(actor_url):
    response = requests.get(
        actor_url,
        headers={
            'Accept': 'application/activity+json',
        }
    )
    response.raise_for_status()
    try:
        return response.json()
    except:
        raise ValueError(
            'Invalid actor payload: {}'.format(response.text))

SYSTEM_ACTORS = {
    'library': {
        'get_actor': lambda: models.Actor(**get_base_system_actor_arguments('library')),
    }
}


def get_base_system_actor_arguments(name):
    preferences = global_preferences_registry.manager()
    return {
        'preferred_username': name,
        'domain': settings.FEDERATION_HOSTNAME,
        'type': 'Person',
        'name': '{}\'s library'.format(settings.FEDERATION_HOSTNAME),
        'manually_approves_followers': True,
        'url': utils.full_url(
            reverse(
                'federation:instance-actors-detail',
                kwargs={'actor': name})),
        'shared_inbox_url': utils.full_url(
            reverse(
                'federation:instance-actors-inbox',
                kwargs={'actor': name})),
        'inbox_url': utils.full_url(
            reverse(
                'federation:instance-actors-inbox',
                kwargs={'actor': name})),
        'outbox_url': utils.full_url(
            reverse(
                'federation:instance-actors-outbox',
                kwargs={'actor': name})),
        'public_key': preferences['federation__public_key'],
        'summary': 'Bot account to federate with {}\'s library'.format(
            settings.FEDERATION_HOSTNAME
        ),
    }
