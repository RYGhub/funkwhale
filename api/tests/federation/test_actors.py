import pytest

from django.urls import reverse
from django.utils import timezone

from rest_framework import exceptions

from funkwhale_api.federation import actors
from funkwhale_api.federation import serializers
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
        'outbox_url': utils.full_url(
            reverse(
                'federation:instance-actors-outbox',
                kwargs={'actor': 'library'})),
        'public_key': 'public_key',
        'summary': 'Bot account to federate with {}\'s library'.format(
        settings.FEDERATION_HOSTNAME),
    }
    actor = actors.SYSTEM_ACTORS['library'].get_actor_instance()
    for key, value in expected.items():
        assert getattr(actor, key) == value


def test_get_test(settings, preferences):
    preferences['federation__public_key'] = 'public_key'
    expected = {
        'preferred_username': 'test',
        'domain': settings.FEDERATION_HOSTNAME,
        'type': 'Person',
        'name': '{}\'s test account'.format(settings.FEDERATION_HOSTNAME),
        'manually_approves_followers': False,
        'url': utils.full_url(
            reverse(
                'federation:instance-actors-detail',
                kwargs={'actor': 'test'})),
        'shared_inbox_url': utils.full_url(
            reverse(
                'federation:instance-actors-inbox',
                kwargs={'actor': 'test'})),
        'inbox_url': utils.full_url(
            reverse(
                'federation:instance-actors-inbox',
                kwargs={'actor': 'test'})),
        'outbox_url': utils.full_url(
            reverse(
                'federation:instance-actors-outbox',
                kwargs={'actor': 'test'})),
        'public_key': 'public_key',
        'summary': 'Bot account to test federation with {}. Send me /ping and I\'ll answer you.'.format(
        settings.FEDERATION_HOSTNAME),
    }
    actor = actors.SYSTEM_ACTORS['test'].get_actor_instance()
    for key, value in expected.items():
        assert getattr(actor, key) == value


def test_test_get_outbox():
    expected = {
    	"@context": [
    		"https://www.w3.org/ns/activitystreams",
    		"https://w3id.org/security/v1",
    		{}
    	],
    	"id": utils.full_url(
            reverse(
                'federation:instance-actors-outbox',
                kwargs={'actor': 'test'})),
    	"type": "OrderedCollection",
    	"totalItems": 0,
    	"orderedItems": []
    }

    data = actors.SYSTEM_ACTORS['test'].get_outbox({}, actor=None)

    assert data == expected


def test_test_post_inbox_requires_authenticated_actor():
    with pytest.raises(exceptions.PermissionDenied):
        actors.SYSTEM_ACTORS['test'].post_inbox({}, actor=None)


def test_test_post_outbox_validates_actor(nodb_factories):
    actor = nodb_factories['federation.Actor']()
    data = {
        'actor': 'noop'
    }
    with pytest.raises(exceptions.ValidationError) as exc_info:
        actors.SYSTEM_ACTORS['test'].post_inbox(data, actor=actor)
        msg = 'The actor making the request do not match'
        assert msg in exc_info.value


def test_test_post_outbox_handles_create_note(mocker, factories):
    deliver = mocker.patch(
        'funkwhale_api.federation.activity.deliver')
    actor = factories['federation.Actor']()
    now = timezone.now()
    mocker.patch('django.utils.timezone.now', return_value=now)
    data = {
        'actor': actor.url,
        'type': 'Create',
        'id': 'http://test.federation/activity',
        'object': {
            'type': 'Note',
            'id': 'http://test.federation/object',
            'content': '<p><a>@mention</a> /ping</p>'
        }
    }
    expected_note = factories['federation.Note'](
        id='https://test.federation/activities/note/{}'.format(
            now.timestamp()
        ),
        content='Pong!',
        published=now.isoformat(),
        inReplyTo=data['object']['id'],
    )
    test_actor = actors.SYSTEM_ACTORS['test'].get_actor_instance()
    expected_activity = {
        'actor': test_actor.url,
        'id': 'https://test.federation/activities/note/{}/activity'.format(
            now.timestamp()
        ),
        'type': 'Create',
        'published': now.isoformat(),
        'object': expected_note
    }
    actors.SYSTEM_ACTORS['test'].post_inbox(data, actor=actor)
    deliver.assert_called_once_with(
        expected_activity,
        to=[actor.url],
        on_behalf_of=actors.SYSTEM_ACTORS['test'].get_actor_instance()
    )
