from django.urls import reverse

from funkwhale_api.federation import keys
from funkwhale_api.federation import models
from funkwhale_api.federation import serializers


def test_actor_serializer_from_ap(db):
    payload = {
    	'id': 'https://test.federation/user',
    	'type': 'Person',
    	'following': 'https://test.federation/user/following',
    	'followers': 'https://test.federation/user/followers',
    	'inbox': 'https://test.federation/user/inbox',
    	'outbox': 'https://test.federation/user/outbox',
    	'preferredUsername': 'user',
    	'name': 'Real User',
    	'summary': 'Hello world',
    	'url': 'https://test.federation/@user',
    	'manuallyApprovesFollowers': False,
    	'publicKey': {
    		'id': 'https://test.federation/user#main-key',
    		'owner': 'https://test.federation/user',
    		'publicKeyPem': 'yolo'
    	},
    	'endpoints': {
    		'sharedInbox': 'https://test.federation/inbox'
    	},
    }

    serializer = serializers.ActorSerializer(data=payload)
    assert serializer.is_valid()

    actor = serializer.build()

    assert actor.url == payload['id']
    assert actor.inbox_url == payload['inbox']
    assert actor.outbox_url == payload['outbox']
    assert actor.shared_inbox_url == payload['endpoints']['sharedInbox']
    assert actor.followers_url == payload['followers']
    assert actor.following_url == payload['following']
    assert actor.public_key == payload['publicKey']['publicKeyPem']
    assert actor.preferred_username == payload['preferredUsername']
    assert actor.name == payload['name']
    assert actor.domain == 'test.federation'
    assert actor.summary == payload['summary']
    assert actor.type == 'Person'
    assert actor.manually_approves_followers == payload['manuallyApprovesFollowers']


def test_actor_serializer_only_mandatory_field_from_ap(db):
    payload = {
    	'id': 'https://test.federation/user',
    	'type': 'Person',
    	'following': 'https://test.federation/user/following',
    	'followers': 'https://test.federation/user/followers',
    	'inbox': 'https://test.federation/user/inbox',
    	'outbox': 'https://test.federation/user/outbox',
    	'preferredUsername': 'user',
    }

    serializer = serializers.ActorSerializer(data=payload)
    assert serializer.is_valid()

    actor = serializer.build()

    assert actor.url == payload['id']
    assert actor.inbox_url == payload['inbox']
    assert actor.outbox_url == payload['outbox']
    assert actor.followers_url == payload['followers']
    assert actor.following_url == payload['following']
    assert actor.preferred_username == payload['preferredUsername']
    assert actor.domain == 'test.federation'
    assert actor.type == 'Person'
    assert actor.manually_approves_followers is None


def test_actor_serializer_to_ap():
    expected = {
        '@context': [
            'https://www.w3.org/ns/activitystreams',
            'https://w3id.org/security/v1',
            {},
        ],
    	'id': 'https://test.federation/user',
    	'type': 'Person',
    	'following': 'https://test.federation/user/following',
    	'followers': 'https://test.federation/user/followers',
    	'inbox': 'https://test.federation/user/inbox',
    	'outbox': 'https://test.federation/user/outbox',
    	'preferredUsername': 'user',
    	'name': 'Real User',
    	'summary': 'Hello world',
    	'manuallyApprovesFollowers': False,
    	'publicKey': {
    		'id': 'https://test.federation/user#main-key',
    		'owner': 'https://test.federation/user',
    		'publicKeyPem': 'yolo'
    	},
    	'endpoints': {
    		'sharedInbox': 'https://test.federation/inbox'
    	},
    }
    ac = models.Actor(
        url=expected['id'],
        inbox_url=expected['inbox'],
        outbox_url=expected['outbox'],
        shared_inbox_url=expected['endpoints']['sharedInbox'],
        followers_url=expected['followers'],
        following_url=expected['following'],
        public_key=expected['publicKey']['publicKeyPem'],
        preferred_username=expected['preferredUsername'],
        name=expected['name'],
        domain='test.federation',
        summary=expected['summary'],
        type='Person',
        manually_approves_followers=False,

    )
    serializer = serializers.ActorSerializer(ac)

    assert serializer.data == expected


def test_webfinger_serializer():
    expected = {
        'subject': 'acct:service@test.federation',
        'links': [
            {
                'rel': 'self',
                'href': 'https://test.federation/federation/instance/actor',
                'type': 'application/activity+json',
            }
        ],
        'aliases': [
            'https://test.federation/federation/instance/actor',
        ]
    }
    actor = models.Actor(
        url=expected['links'][0]['href'],
        preferred_username='service',
        domain='test.federation',
    )
    serializer = serializers.ActorWebfingerSerializer(actor)

    assert serializer.data == expected


def test_follow_serializer_to_ap(factories):
    follow = factories['federation.Follow'](local=True)
    serializer = serializers.FollowSerializer(follow)

    expected = {
        '@context': [
            'https://www.w3.org/ns/activitystreams',
            'https://w3id.org/security/v1',
            {},
        ],
        'id': follow.get_federation_url(),
        'type': 'Follow',
        'actor': follow.actor.url,
        'object': follow.target.url,
    }

    assert serializer.data == expected
