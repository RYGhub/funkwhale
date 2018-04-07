import arrow
import pytest
import uuid

from django.urls import reverse
from django.utils import timezone

from rest_framework import exceptions

from funkwhale_api.federation import actors
from funkwhale_api.federation import models
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


def test_get_library(db, settings, mocker):
    get_key_pair = mocker.patch(
        'funkwhale_api.federation.keys.get_key_pair',
        return_value=(b'private', b'public'))
    expected = {
        'preferred_username': 'library',
        'domain': settings.FEDERATION_HOSTNAME,
        'type': 'Person',
        'name': '{}\'s library'.format(settings.FEDERATION_HOSTNAME),
        'manually_approves_followers': True,
        'public_key': 'public',
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
        'summary': 'Bot account to federate with {}\'s library'.format(
        settings.FEDERATION_HOSTNAME),
    }
    actor = actors.SYSTEM_ACTORS['library'].get_actor_instance()
    for key, value in expected.items():
        assert getattr(actor, key) == value


def test_get_test(db, mocker, settings):
    get_key_pair = mocker.patch(
        'funkwhale_api.federation.keys.get_key_pair',
        return_value=(b'private', b'public'))
    expected = {
        'preferred_username': 'test',
        'domain': settings.FEDERATION_HOSTNAME,
        'type': 'Person',
        'name': '{}\'s test account'.format(settings.FEDERATION_HOSTNAME),
        'manually_approves_followers': False,
        'public_key': 'public',
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


def test_test_post_inbox_handles_create_note(
        settings, mocker, factories):
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
    test_actor = actors.SYSTEM_ACTORS['test'].get_actor_instance()
    expected_note = factories['federation.Note'](
        id='https://test.federation/activities/note/{}'.format(
            now.timestamp()
        ),
        content='Pong!',
        published=now.isoformat(),
        inReplyTo=data['object']['id'],
        cc=[],
        summary=None,
        sensitive=False,
        attributedTo=test_actor.url,
        attachment=[],
        to=[actor.url],
        url='https://{}/activities/note/{}'.format(
            settings.FEDERATION_HOSTNAME, now.timestamp()
        ),
        tag=[{
            'href': actor.url,
            'name': actor.mention_username,
            'type': 'Mention',
        }]
    )
    expected_activity = {
        '@context': serializers.AP_CONTEXT,
        'actor': test_actor.url,
        'id': 'https://{}/activities/note/{}/activity'.format(
            settings.FEDERATION_HOSTNAME, now.timestamp()
        ),
        'to': actor.url,
        'type': 'Create',
        'published': now.isoformat(),
        'object': expected_note,
        'cc': [],
    }
    actors.SYSTEM_ACTORS['test'].post_inbox(data, actor=actor)
    deliver.assert_called_once_with(
        expected_activity,
        to=[actor.url],
        on_behalf_of=actors.SYSTEM_ACTORS['test'].get_actor_instance()
    )


def test_getting_actor_instance_persists_in_db(db):
    test = actors.SYSTEM_ACTORS['test'].get_actor_instance()
    from_db = models.Actor.objects.get(url=test.url)

    for f in test._meta.fields:
        assert getattr(from_db, f.name) == getattr(test, f.name)


@pytest.mark.parametrize('username,domain,expected', [
    ('test', 'wrongdomain.com', False),
    ('notsystem', '', False),
    ('test', '', True),
])
def test_actor_is_system(
        username, domain, expected, nodb_factories, settings):
    if not domain:
        domain = settings.FEDERATION_HOSTNAME

    actor = nodb_factories['federation.Actor'](
        preferred_username=username,
        domain=domain,
    )
    assert actor.is_system is expected


@pytest.mark.parametrize('username,domain,expected', [
    ('test', 'wrongdomain.com', None),
    ('notsystem', '', None),
    ('test', '', actors.SYSTEM_ACTORS['test']),
])
def test_actor_is_system(
        username, domain, expected, nodb_factories, settings):
    if not domain:
        domain = settings.FEDERATION_HOSTNAME
    actor = nodb_factories['federation.Actor'](
        preferred_username=username,
        domain=domain,
    )
    assert actor.system_conf == expected


@pytest.mark.parametrize('value', [False, True])
def test_library_actor_manually_approves_based_on_setting(
        value, settings):
    settings.FEDERATION_MUSIC_NEEDS_APPROVAL = value
    library_conf = actors.SYSTEM_ACTORS['library']
    assert library_conf.manually_approves_followers is value


def test_system_actor_handle(mocker, nodb_factories):
    handler = mocker.patch(
        'funkwhale_api.federation.actors.TestActor.handle_create')
    actor = nodb_factories['federation.Actor']()
    activity = nodb_factories['federation.Activity'](
        type='Create', actor=actor.url)
    serializer = serializers.ActivitySerializer(
        data=activity
    )
    assert serializer.is_valid()
    actors.SYSTEM_ACTORS['test'].handle(activity, actor)
    handler.assert_called_once_with(activity, actor)


def test_test_actor_handles_follow(
        settings, mocker, factories):
    deliver = mocker.patch(
        'funkwhale_api.federation.activity.deliver')
    actor = factories['federation.Actor']()
    now = timezone.now()
    mocker.patch('django.utils.timezone.now', return_value=now)
    accept_follow = mocker.patch(
        'funkwhale_api.federation.activity.accept_follow')
    test_actor = actors.SYSTEM_ACTORS['test'].get_actor_instance()
    data = {
        'actor': actor.url,
        'type': 'Follow',
        'id': 'http://test.federation/user#follows/267',
        'object': test_actor.url,
    }
    uid = uuid.uuid4()
    mocker.patch('uuid.uuid4', return_value=uid)
    expected_follow = {
        '@context': serializers.AP_CONTEXT,
        'actor': test_actor.url,
        'id': test_actor.url + '#follows/{}'.format(uid),
        'object': actor.url,
        'type': 'Follow'
    }

    actors.SYSTEM_ACTORS['test'].post_inbox(data, actor=actor)
    accept_follow.assert_called_once_with(
        test_actor, data, actor
    )
    expected_calls = [
        mocker.call(
            expected_follow,
            to=[actor.url],
            on_behalf_of=test_actor,
        )
    ]
    deliver.assert_has_calls(expected_calls)


def test_test_actor_handles_undo_follow(
        settings, mocker, factories):
    deliver = mocker.patch(
        'funkwhale_api.federation.activity.deliver')
    test_actor = actors.SYSTEM_ACTORS['test'].get_actor_instance()
    follow = factories['federation.Follow'](target=test_actor)
    reverse_follow = factories['federation.Follow'](
        actor=test_actor, target=follow.actor)
    follow_serializer = serializers.FollowSerializer(follow)
    reverse_follow_serializer = serializers.FollowSerializer(
        reverse_follow)
    undo = {
        '@context': serializers.AP_CONTEXT,
        'type': 'Undo',
        'id': follow_serializer.data['id'] + '/undo',
        'actor': follow.actor.url,
        'object': follow_serializer.data,
    }
    expected_undo = {
        '@context': serializers.AP_CONTEXT,
        'type': 'Undo',
        'id': reverse_follow_serializer.data['id'] + '/undo',
        'actor': reverse_follow.actor.url,
        'object': reverse_follow_serializer.data,
    }

    actors.SYSTEM_ACTORS['test'].post_inbox(undo, actor=follow.actor)
    deliver.assert_called_once_with(
        expected_undo,
        to=[follow.actor.url],
        on_behalf_of=test_actor,)

    assert models.Follow.objects.count() == 0


def test_library_actor_handles_follow_manual_approval(
        settings, mocker, factories):
    settings.FEDERATION_MUSIC_NEEDS_APPROVAL = True
    actor = factories['federation.Actor']()
    now = timezone.now()
    mocker.patch('django.utils.timezone.now', return_value=now)
    library_actor = actors.SYSTEM_ACTORS['library'].get_actor_instance()
    data = {
        'actor': actor.url,
        'type': 'Follow',
        'id': 'http://test.federation/user#follows/267',
        'object': library_actor.url,
    }

    library_actor.system_conf.post_inbox(data, actor=actor)
    fr = library_actor.received_follow_requests.first()

    assert library_actor.received_follow_requests.count() == 1
    assert fr.target == library_actor
    assert fr.actor == actor
    assert fr.approved is None


def test_library_actor_handles_follow_auto_approval(
        settings, mocker, factories):
    settings.FEDERATION_MUSIC_NEEDS_APPROVAL = False
    actor = factories['federation.Actor']()
    accept_follow = mocker.patch(
        'funkwhale_api.federation.activity.accept_follow')
    library_actor = actors.SYSTEM_ACTORS['library'].get_actor_instance()
    data = {
        'actor': actor.url,
        'type': 'Follow',
        'id': 'http://test.federation/user#follows/267',
        'object': library_actor.url,
    }
    library_actor.system_conf.post_inbox(data, actor=actor)

    assert library_actor.received_follow_requests.count() == 0
    accept_follow.assert_called_once_with(
        library_actor, data, actor
    )


def test_library_actor_handle_create_audio_no_library(mocker, factories):
    # when we receive inbox create audio, we should not do anything
    # if we don't have a configured library matching the sender
    mocked_create = mocker.patch(
        'funkwhale_api.federation.serializers.AudioSerializer.create'
    )
    actor = factories['federation.Actor']()
    library_actor = actors.SYSTEM_ACTORS['library'].get_actor_instance()
    data = {
        'actor': actor.url,
        'type': 'Create',
        'id': 'http://test.federation/audio/create',
        'object': {
            'id': 'https://batch.import',
            'type': 'Collection',
            'totalItems': 2,
            'items': factories['federation.Audio'].create_batch(size=2)
        },
    }
    library_actor.system_conf.post_inbox(data, actor=actor)

    mocked_create.assert_not_called()
    models.LibraryTrack.objects.count() == 0


def test_library_actor_handle_create_audio_no_library_enabled(
        mocker, factories):
    # when we receive inbox create audio, we should not do anything
    # if we don't have an enabled library
    mocked_create = mocker.patch(
        'funkwhale_api.federation.serializers.AudioSerializer.create'
    )
    disabled_library = factories['federation.Library'](
        federation_enabled=False)
    actor = disabled_library.actor
    library_actor = actors.SYSTEM_ACTORS['library'].get_actor_instance()
    data = {
        'actor': actor.url,
        'type': 'Create',
        'id': 'http://test.federation/audio/create',
        'object': {
            'id': 'https://batch.import',
            'type': 'Collection',
            'totalItems': 2,
            'items': factories['federation.Audio'].create_batch(size=2)
        },
    }
    library_actor.system_conf.post_inbox(data, actor=actor)

    mocked_create.assert_not_called()
    models.LibraryTrack.objects.count() == 0


def test_library_actor_handle_create_audio(mocker, factories):
    library_actor = actors.SYSTEM_ACTORS['library'].get_actor_instance()
    remote_library = factories['federation.Library'](
        federation_enabled=True
    )

    data = {
        'actor': remote_library.actor.url,
        'type': 'Create',
        'id': 'http://test.federation/audio/create',
        'object': {
            'id': 'https://batch.import',
            'type': 'Collection',
            'totalItems': 2,
            'items': factories['federation.Audio'].create_batch(size=2)
        },
    }

    library_actor.system_conf.post_inbox(data, actor=remote_library.actor)

    lts = list(remote_library.tracks.order_by('id'))

    assert len(lts) == 2

    for i, a in enumerate(data['object']['items']):
        lt = lts[i]
        assert lt.pk is not None
        assert lt.url == a['id']
        assert lt.library == remote_library
        assert lt.audio_url == a['url']['href']
        assert lt.audio_mimetype == a['url']['mediaType']
        assert lt.metadata == a['metadata']
        assert lt.title == a['metadata']['recording']['title']
        assert lt.artist_name == a['metadata']['artist']['name']
        assert lt.album_title == a['metadata']['release']['title']
        assert lt.published_date == arrow.get(a['published'])
