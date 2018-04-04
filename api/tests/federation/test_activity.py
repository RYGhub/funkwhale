import uuid

from funkwhale_api.federation import activity


def test_deliver(nodb_factories, r_mock, mocker):
    to = nodb_factories['federation.Actor']()
    mocker.patch(
        'funkwhale_api.federation.actors.get_actor',
        return_value=to)
    sender = nodb_factories['federation.Actor']()
    ac = {
        'id': 'http://test.federation/activity',
        'type': 'Create',
        'actor': sender.url,
        'object': {
            'id': 'http://test.federation/note',
            'type': 'Note',
            'content': 'Hello',
        }
    }

    r_mock.post(to.inbox_url)

    activity.deliver(
        ac,
        to=[to.url],
        on_behalf_of=sender,
    )
    request = r_mock.request_history[0]

    assert r_mock.called is True
    assert r_mock.call_count == 1
    assert request.url == to.inbox_url
    assert request.headers['content-type'] == 'application/activity+json'


def test_accept_follow(mocker, factories):
    deliver = mocker.patch(
        'funkwhale_api.federation.activity.deliver')
    actor = factories['federation.Actor']()
    target = factories['federation.Actor'](local=True)
    follow = {
        'actor': actor.url,
        'type': 'Follow',
        'id': 'http://test.federation/user#follows/267',
        'object': target.url,
    }
    uid = uuid.uuid4()
    mocker.patch('uuid.uuid4', return_value=uid)
    expected_accept = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
            {}
        ],
        "id": target.url + '#accepts/follows/{}'.format(uid),
        "type": "Accept",
        "actor": target.url,
        "object": {
            "id": follow['id'],
            "type": "Follow",
            "actor": actor.url,
            "object": target.url
        },
    }
    activity.accept_follow(
        target, follow, actor
    )
    deliver.assert_called_once_with(
        expected_accept, to=[actor.url], on_behalf_of=target
    )
    follow_instance = actor.emitted_follows.first()
    assert follow_instance.target == target
