
import pytest

from funkwhale_api.federation import activity, api_serializers, serializers, tasks


def test_receive_validates_basic_attributes_and_stores_activity(factories, now, mocker):
    mocked_dispatch = mocker.patch("funkwhale_api.common.utils.on_commit")
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
    assert copy.type == "Noop"
    mocked_dispatch.assert_called_once_with(
        tasks.dispatch_inbox.delay, activity_id=copy.pk
    )

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


def test_inbox_routing(factories, mocker):
    object = factories["music.Artist"]()
    target = factories["music.Artist"]()
    router = activity.InboxRouter()
    a = factories["federation.Activity"](type="Follow")

    handler_payload = {}
    handler_context = {}

    def handler(payload, context):
        handler_payload.update(payload)
        handler_context.update(context)
        return {"target": target, "object": object}

    router.connect({"type": "Follow"}, handler)

    good_message = {"type": "Follow"}
    router.dispatch(good_message, context={"activity": a})

    assert handler_payload == good_message
    assert handler_context == {"activity": a}

    a.refresh_from_db()

    assert a.object == object
    assert a.target == target


def test_inbox_routing_send_to_channel(factories, mocker):
    group_send = mocker.patch("funkwhale_api.common.channels.group_send")
    a = factories["federation.Activity"](type="Follow")
    ii = factories["federation.InboxItem"](actor__local=True)

    router = activity.InboxRouter()
    handler = mocker.stub()
    router.connect({"type": "Follow"}, handler)
    good_message = {"type": "Follow"}
    router.dispatch(
        good_message, context={"activity": a, "inbox_items": ii.__class__.objects.all()}
    )

    ii.refresh_from_db()

    assert ii.is_delivered is True

    group_send.assert_called_once_with(
        "user.{}.inbox".format(ii.actor.user.pk),
        {
            "type": "event.send",
            "text": "",
            "data": {
                "type": "inbox.item_added",
                "item": api_serializers.InboxItemSerializer(ii).data,
            },
        },
    )


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
                "to": [r1],
                "cc": [r2, activity.PUBLIC_ADDRESS],
            },
            "actor": actor,
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
