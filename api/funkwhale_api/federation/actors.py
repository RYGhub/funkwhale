import requests
import xml

from django.urls import reverse
from django.conf import settings

from rest_framework.exceptions import PermissionDenied

from dynamic_preferences.registries import global_preferences_registry

from . import activity
from . import models
from . import serializers
from . import utils


def remove_tags(text):
    return ''.join(xml.etree.ElementTree.fromstring(text).itertext())


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


class SystemActor(object):
    additional_attributes = {}

    def get_actor_instance(self):
        a = models.Actor(
            **self.get_instance_argument(
                self.id,
                name=self.name,
                summary=self.summary,
                **self.additional_attributes
            )
        )
        a.pk = self.id
        return a

    def get_instance_argument(self, id, name, summary, **kwargs):
        preferences = global_preferences_registry.manager()
        p = {
            'preferred_username': id,
            'domain': settings.FEDERATION_HOSTNAME,
            'type': 'Person',
            'name': name.format(host=settings.FEDERATION_HOSTNAME),
            'manually_approves_followers': True,
            'url': utils.full_url(
                reverse(
                    'federation:instance-actors-detail',
                    kwargs={'actor': id})),
            'shared_inbox_url': utils.full_url(
                reverse(
                    'federation:instance-actors-inbox',
                    kwargs={'actor': id})),
            'inbox_url': utils.full_url(
                reverse(
                    'federation:instance-actors-inbox',
                    kwargs={'actor': id})),
            'outbox_url': utils.full_url(
                reverse(
                    'federation:instance-actors-outbox',
                    kwargs={'actor': id})),
            'public_key': preferences['federation__public_key'],
            'summary': summary.format(host=settings.FEDERATION_HOSTNAME)
        }
        p.update(kwargs)
        return p

    def get_inbox(self, data, actor=None):
        raise NotImplementedError

    def post_inbox(self, data, actor=None):
        raise NotImplementedError

    def get_outbox(self, data, actor=None):
        raise NotImplementedError

    def post_outbox(self, data, actor=None):
        raise NotImplementedError


class LibraryActor(SystemActor):
    id = 'library'
    name = '{host}\'s library'
    summary = 'Bot account to federate with {host}\'s library'
    additional_attributes = {
        'manually_approves_followers': True
    }


class TestActor(SystemActor):
    id = 'test'
    name = '{host}\'s test account'
    summary = (
        'Bot account to test federation with {host}. '
        'Send me /ping and I\'ll answer you.'
    )
    additional_attributes = {
        'manually_approves_followers': False
    }

    def get_outbox(self, data, actor=None):
        return {
        	"@context": [
        		"https://www.w3.org/ns/activitystreams",
        		"https://w3id.org/security/v1",
        		{}
        	],
        	"id": utils.full_url(
                reverse(
                    'federation:instance-actors-outbox',
                    kwargs={'actor': self.id})),
        	"type": "OrderedCollection",
        	"totalItems": 0,
        	"orderedItems": []
        }

    def post_inbox(self, data, actor=None):
        if actor is None:
            raise PermissionDenied('Actor not authenticated')

        serializer = serializers.ActivitySerializer(
            data=data, context={'actor': actor})
        serializer.is_valid(raise_exception=True)

        ac = serializer.validated_data
        if ac['type'] == 'Create' and ac['object']['type'] == 'Note':
            # we received a toot \o/
            command = self.parse_command(ac['object']['content'])
            if command == 'ping':
                activity.deliver(
                    content='Pong!',
                    to=[ac['actor']],
                    on_behalf_of=self.get_actor_instance())

    def parse_command(self, message):
        """
        Remove any links or fancy markup to extract /command from
        a note message.
        """
        raw = remove_tags(message)
        try:
            return raw.split('/')[1]
        except IndexError:
            return


SYSTEM_ACTORS = {
    'library': LibraryActor(),
    'test': TestActor(),
}
