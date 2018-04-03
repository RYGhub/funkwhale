import logging
import requests
import uuid
import xml

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from rest_framework.exceptions import PermissionDenied

from dynamic_preferences.registries import global_preferences_registry

from . import activity
from . import models
from . import serializers
from . import utils

logger = logging.getLogger(__name__)


def remove_tags(text):
    logger.debug('Removing tags from %s', text)
    return ''.join(xml.etree.ElementTree.fromstring('<div>{}</div>'.format(text)).itertext())


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

def get_actor(actor_url):
    data = get_actor_data(actor_url)
    serializer = serializers.ActorSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    return serializer.build()


class SystemActor(object):
    additional_attributes = {}
    manually_approves_followers = False

    def get_actor_instance(self):
        args = self.get_instance_argument(
            self.id,
            name=self.name,
            summary=self.summary,
            **self.additional_attributes
        )
        url = args.pop('url')
        a, created = models.Actor.objects.get_or_create(
            url=url,
            defaults=args,
        )
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
            'private_key': preferences['federation__private_key'],
            'summary': summary.format(host=settings.FEDERATION_HOSTNAME)
        }
        p.update(kwargs)
        return p

    def get_inbox(self, data, actor=None):
        raise NotImplementedError

    def post_inbox(self, data, actor=None):
        return self.handle(data, actor=actor)

    def get_outbox(self, data, actor=None):
        raise NotImplementedError

    def post_outbox(self, data, actor=None):
        raise NotImplementedError

    def handle(self, data, actor=None):
        """
        Main entrypoint for handling activities posted to the
        actor's inbox
        """
        logger.info('Received activity on %s inbox', self.id)

        if actor is None:
            raise PermissionDenied('Actor not authenticated')

        serializer = serializers.ActivitySerializer(
            data=data, context={'actor': actor})
        serializer.is_valid(raise_exception=True)

        ac = serializer.data
        try:
            handler = getattr(
                self, 'handle_{}'.format(ac['type'].lower()))
        except (KeyError, AttributeError):
            logger.debug(
                'No handler for activity %s', ac['type'])
            return

        return handler(data, actor)


class LibraryActor(SystemActor):
    id = 'library'
    name = '{host}\'s library'
    summary = 'Bot account to federate with {host}\'s library'
    additional_attributes = {
        'manually_approves_followers': True
    }
    @property
    def manually_approves_followers(self):
        return settings.FEDERATION_MUSIC_NEEDS_APPROVAL


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
    manually_approves_followers = False

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

    def handle_create(self, ac, sender):
        if ac['object']['type'] != 'Note':
            return

        # we received a toot \o/
        command = self.parse_command(ac['object']['content'])
        logger.debug('Parsed command: %s', command)
        if command != 'ping':
            return

        now = timezone.now()
        test_actor = self.get_actor_instance()
        reply_url = 'https://{}/activities/note/{}'.format(
            settings.FEDERATION_HOSTNAME, now.timestamp()
        )
        reply_content = '{} Pong!'.format(
            sender.mention_username
        )
        reply_activity = {
            "@context": [
        		"https://www.w3.org/ns/activitystreams",
        		"https://w3id.org/security/v1",
        		{}
        	],
            'type': 'Create',
            'actor': test_actor.url,
            'id': '{}/activity'.format(reply_url),
            'published': now.isoformat(),
            'to': ac['actor'],
            'cc': [],
            'object': {
                'type': 'Note',
                'content': 'Pong!',
                'summary': None,
                'published': now.isoformat(),
                'id': reply_url,
                'inReplyTo': ac['object']['id'],
                'sensitive': False,
                'url': reply_url,
                'to': [ac['actor']],
                'attributedTo': test_actor.url,
                'cc': [],
                'attachment': [],
                'tag': [{
                    "type": "Mention",
                    "href": ac['actor'],
                    "name": sender.mention_username
                }]
            }
        }
        activity.deliver(
            reply_activity,
            to=[ac['actor']],
            on_behalf_of=test_actor)

    def handle_follow(self, ac, sender):
        # on a follow we:
        # 1. send the accept answer
        # 2. follow back
        #
        test_actor = self.get_actor_instance()
        accept_uuid = uuid.uuid4()
        accept = activity.get_accept_follow(
            accept_id=accept_uuid,
            accept_actor=test_actor,
            follow=ac,
            follow_actor=sender)
        activity.deliver(
            accept,
            to=[ac['actor']],
            on_behalf_of=test_actor)
        models.Follow.objects.get_or_create(
            actor=sender,
            target=test_actor,
        )
        follow_uuid = uuid.uuid4()
        follow = activity.get_follow(
            follow_id=follow_uuid,
            follower=test_actor,
            followed=sender)
        activity.deliver(
            follow,
            to=[ac['actor']],
            on_behalf_of=test_actor)

    def handle_undo(self, ac, sender):
        if ac['object']['type'] != 'Follow':
            return

        if ac['object']['actor'] != sender.url:
            # not the same actor, permission issue
            return

        test_actor = self.get_actor_instance()
        models.Follow.objects.filter(
            actor=sender,
            target=test_actor,
        ).delete()
        # we also unfollow the sender, if possible
        try:
            follow = models.Follow.objects.get(
                target=sender,
                actor=test_actor,
            )
        except models.Follow.DoesNotExist:
            return
        undo = {
            '@context': serializers.AP_CONTEXT,
            'type': 'Undo',
            'id': follow.get_federation_url() + '/undo',
            'actor': test_actor.url,
            'object': serializers.FollowSerializer(follow).data,
        }
        follow.delete()
        activity.deliver(
            undo,
            to=[sender.url],
            on_behalf_of=test_actor)

SYSTEM_ACTORS = {
    'library': LibraryActor(),
    'test': TestActor(),
}
