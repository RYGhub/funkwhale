import logging
import json
import requests_http_signature
import uuid

from django.conf import settings

from funkwhale_api.common import session
from funkwhale_api.common import utils as funkwhale_utils

from . import models
from . import serializers
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
        response = session.get_session().post(
            auth=auth,
            json=activity,
            url=recipient_actor.inbox_url,
            timeout=5,
            verify=settings.EXTERNAL_REQUESTS_VERIFY_SSL,
            headers={
                'Content-Type': 'application/activity+json'
            }
        )
        response.raise_for_status()
        logger.debug('Remote answered with %s', response.status_code)


def accept_follow(follow):
    serializer = serializers.AcceptFollowSerializer(follow)
    deliver(
        serializer.data,
        to=[follow.actor.url],
        on_behalf_of=follow.target)
