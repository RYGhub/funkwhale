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
