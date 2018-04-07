import logging
import json
import requests
import requests_http_signature
import uuid

from . import models
from . import signing

logger = logging.getLogger(__name__)

ACTIVITY_TYPES = [
    'Accept',
    'Add',
    'Announce',
    'Arrive',
    'Block',
    'Create',
    'Delete',
    'Dislike',
    'Flag',
    'Follow',
    'Ignore',
    'Invite',
    'Join',
    'Leave',
    'Like',
    'Listen',
    'Move',
    'Offer',
    'Question',
    'Reject',
    'Read',
    'Remove',
    'TentativeReject',
    'TentativeAccept',
    'Travel',
    'Undo',
    'Update',
    'View',
]


OBJECT_TYPES = [
    'Article',
    'Audio',
    'Collection',
    'Document',
    'Event',
    'Image',
    'Note',
    'OrderedCollection',
    'Page',
    'Place',
    'Profile',
    'Relationship',
    'Tombstone',
    'Video',
] + ACTIVITY_TYPES


def deliver(activity, on_behalf_of, to=[]):
    from . import actors
    logger.info('Preparing activity delivery to %s', to)
    auth = signing.get_auth(
        on_behalf_of.private_key, on_behalf_of.private_key_id)
    for url in to:
        recipient_actor = actors.get_actor(url)
        logger.debug('delivering to %s', recipient_actor.inbox_url)
        logger.debug('activity content: %s', json.dumps(activity))
        response = requests.post(
            auth=auth,
            json=activity,
            url=recipient_actor.inbox_url,
            headers={
                'Content-Type': 'application/activity+json'
            }
        )
        response.raise_for_status()
        logger.debug('Remote answered with %s', response.status_code)


def get_follow(follow_id, follower, followed):
    return {
        '@context': [
            'https://www.w3.org/ns/activitystreams',
            'https://w3id.org/security/v1',
            {}
        ],
        'actor': follower.url,
        'id': follower.url + '#follows/{}'.format(follow_id),
        'object': followed.url,
        'type': 'Follow'
    }


def get_undo(id, actor, object):
    return {
        '@context': [
            'https://www.w3.org/ns/activitystreams',
            'https://w3id.org/security/v1',
            {}
        ],
        'type': 'Undo',
        'id': id + '/undo',
        'actor': actor.url,
        'object': object,
    }


def get_accept_follow(accept_id, accept_actor, follow, follow_actor):
    return {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
            {}
        ],
        "id": accept_actor.url + '#accepts/follows/{}'.format(
            accept_id),
        "type": "Accept",
        "actor": accept_actor.url,
        "object": {
            "id": follow['id'],
            "type": "Follow",
            "actor": follow_actor.url,
            "object": accept_actor.url
        },
    }


def accept_follow(target, follow, actor):
    accept_uuid = uuid.uuid4()
    accept = get_accept_follow(
        accept_id=accept_uuid,
        accept_actor=target,
        follow=follow,
        follow_actor=actor)
    deliver(
        accept,
        to=[actor.url],
        on_behalf_of=target)
    return models.Follow.objects.get_or_create(
        actor=actor,
        target=target,
    )
