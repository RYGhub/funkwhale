
from funkwhale_api.federation import activity
from funkwhale_api.federation import serializers


def test_deliver(factories, r_mock, mocker, settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    to = factories["federation.Actor"]()
    mocker.patch("funkwhale_api.federation.actors.get_actor", return_value=to)
    sender = factories["federation.Actor"]()
    ac = {
        "id": "http://test.federation/activity",
        "type": "Create",
        "actor": sender.url,
        "object": {
            "id": "http://test.federation/note",
            "type": "Note",
            "content": "Hello",
        },
    }

    r_mock.post(to.inbox_url)

    activity.deliver(ac, to=[to.url], on_behalf_of=sender)
    request = r_mock.request_history[0]

    assert r_mock.called is True
    assert r_mock.call_count == 1
    assert request.url == to.inbox_url
    assert request.headers["content-type"] == "application/activity+json"


def test_accept_follow(mocker, factories):
    deliver = mocker.patch("funkwhale_api.federation.activity.deliver")
    follow = factories["federation.Follow"](approved=None)
    expected_accept = serializers.AcceptFollowSerializer(follow).data
    activity.accept_follow(follow)
    deliver.assert_called_once_with(
        expected_accept, to=[follow.actor.url], on_behalf_of=follow.target
    )
