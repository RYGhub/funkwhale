
import pytest

from funkwhale_api.federation import activity, serializers, tasks


def test_accept_follow(mocker, factories):
    deliver = mocker.patch("funkwhale_api.federation.activity.deliver")
    follow = factories["federation.Follow"](approved=None)
    expected_accept = serializers.AcceptFollowSerializer(follow).data
    activity.accept_follow(follow)
    deliver.assert_called_once_with(
        expected_accept, to=[follow.actor.fid], on_behalf_of=follow.target
    )


def test_receive_validates_basic_attributes_and_stores_activity(factories, now, mocker):
    mocked_dispatch = mocker.patch(
        "funkwhale_api.federation.tasks.dispatch_inbox.delay"
    )
    local_actor = factories["users.User"]().create_actor()
    remote_actor = factories["federation.Actor"]()
    another_actor = factories["federation.Actor"]()
    a = {
        "@context": [],
        "actor": remote_actor.fid,
        "type": "Noop",
        "id": "https://test.activity",
        "to": [local_actor.fid],
        "cc": [another_actor.fid, activity.PUBLIC_ADDRESS],
    }

    copy = activity.receive(activity=a, on_behalf_of=remote_actor)

    assert copy.payload == a
    assert copy.creation_date >= now
    assert copy.actor == remote_actor
    assert copy.fid == a["id"]
    mocked_dispatch.assert_called_once_with(activity_id=copy.pk)

    inbox_item = copy.inbox_items.get(actor__fid=local_actor.fid)
    assert inbox_item.is_delivered is False


def test_receive_invalid_data(factories):
    remote_actor = factories["federation.Actor"]()
    a = {"@context": [], "actor": remote_actor.fid, "id": "https://test.activity"}

    with pytest.raises(serializers.serializers.ValidationError):
        activity.receive(activity=a, on_behalf_of=remote_actor)


def test_receive_actor_mismatch(factories):
    remote_actor = factories["federation.Actor"]()
    a = {
        "@context": [],
        "type": "Noop",
        "actor": "https://hello",
        "id": "https://test.activity",
    }

    with pytest.raises(serializers.serializers.ValidationError):
        activity.receive(activity=a, on_behalf_of=remote_actor)


def test_inbox_routing(mocker):
    router = activity.InboxRouter()

    handler = mocker.stub(name="handler")
    router.connect({"type": "Follow"}, handler)

    good_message = {"type": "Follow"}
    router.dispatch(good_message, context={})

    handler.assert_called_once_with(good_message, context={})


@pytest.mark.parametrize(
    "route,payload,expected",
    [
        ({"type": "Follow"}, {"type": "Follow"}, True),
        ({"type": "Follow"}, {"type": "Noop"}, False),
        ({"type": "Follow"}, {"type": "Follow", "id": "https://hello"}, True),
    ],
)
def test_route_matching(route, payload, expected):
    assert activity.match_route(route, payload) is expected


def test_outbox_router_dispatch(mocker, factories, now):
    router = activity.OutboxRouter()
    recipient = factories["federation.Actor"]()
    actor = factories["federation.Actor"]()
    r1 = factories["federation.Actor"]()
    r2 = factories["federation.Actor"]()
    mocked_dispatch = mocker.patch("funkwhale_api.common.utils.on_commit")

    def handler(context):
        yield {
            "payload": {
                "type": "Noop",
                "actor": actor.fid,
                "summary": context["summary"],
            },
            "actor": actor,
            "to": [r1],
            "cc": [r2, activity.PUBLIC_ADDRESS],
        }

    router.connect({"type": "Noop"}, handler)
    activities = router.dispatch({"type": "Noop"}, {"summary": "hello"})
    a = activities[0]

    mocked_dispatch.assert_called_once_with(
        tasks.dispatch_outbox.delay, activity_id=a.pk
    )

    assert a.payload == {
        "type": "Noop",
        "actor": actor.fid,
        "summary": "hello",
        "to": [r1.fid],
        "cc": [r2.fid, activity.PUBLIC_ADDRESS],
    }
    assert a.actor == actor
    assert a.creation_date >= now
    assert a.uuid is not None

    for recipient, type in [(r1, "to"), (r2, "cc")]:
        item = a.inbox_items.get(actor=recipient)
        assert item.is_delivered is False
        assert item.last_delivery_date is None
        assert item.delivery_attempts == 0
        assert item.type == type
