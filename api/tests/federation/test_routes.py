import pytest

from funkwhale_api.federation import routes, serializers


@pytest.mark.parametrize(
    "route,handler",
    [
        ({"type": "Follow"}, routes.inbox_follow),
        ({"type": "Accept"}, routes.inbox_accept),
    ],
)
def test_inbox_routes(route, handler):
    for r, h in routes.inbox.routes:
        if r == route:
            assert h == handler
            return

    assert False, "Inbox route {} not found".format(route)


@pytest.mark.parametrize(
    "route,handler",
    [
        ({"type": "Accept"}, routes.outbox_accept),
        ({"type": "Follow"}, routes.outbox_follow),
    ],
)
def test_outbox_routes(route, handler):
    for r, h in routes.outbox.routes:
        if r == route:
            assert h == handler
            return

    assert False, "Outbox route {} not found".format(route)


def test_inbox_follow_library_autoapprove(factories, mocker):
    mocked_outbox_dispatch = mocker.patch(
        "funkwhale_api.federation.activity.OutboxRouter.dispatch"
    )

    local_actor = factories["users.User"]().create_actor()
    remote_actor = factories["federation.Actor"]()
    library = factories["music.Library"](actor=local_actor, privacy_level="everyone")
    ii = factories["federation.InboxItem"](actor=local_actor)

    payload = {
        "type": "Follow",
        "id": "https://test.follow",
        "actor": remote_actor.fid,
        "object": library.fid,
    }

    result = routes.inbox_follow(
        payload,
        context={"actor": remote_actor, "inbox_items": [ii], "raise_exception": True},
    )
    follow = library.received_follows.latest("id")

    assert result["object"] == library
    assert result["related_object"] == follow

    assert follow.fid == payload["id"]
    assert follow.actor == remote_actor
    assert follow.approved is True

    mocked_outbox_dispatch.assert_called_once_with(
        {"type": "Accept"}, context={"follow": follow}
    )


def test_inbox_follow_library_manual_approve(factories, mocker):
    mocked_outbox_dispatch = mocker.patch(
        "funkwhale_api.federation.activity.OutboxRouter.dispatch"
    )

    local_actor = factories["users.User"]().create_actor()
    remote_actor = factories["federation.Actor"]()
    library = factories["music.Library"](actor=local_actor, privacy_level="me")
    ii = factories["federation.InboxItem"](actor=local_actor)

    payload = {
        "type": "Follow",
        "id": "https://test.follow",
        "actor": remote_actor.fid,
        "object": library.fid,
    }

    result = routes.inbox_follow(
        payload,
        context={"actor": remote_actor, "inbox_items": [ii], "raise_exception": True},
    )
    follow = library.received_follows.latest("id")

    assert result["object"] == library
    assert result["related_object"] == follow

    assert follow.fid == payload["id"]
    assert follow.actor == remote_actor
    assert follow.approved is None

    mocked_outbox_dispatch.assert_not_called()


def test_outbox_accept(factories, mocker):
    remote_actor = factories["federation.Actor"]()
    follow = factories["federation.LibraryFollow"](actor=remote_actor)

    activity = list(routes.outbox_accept({"follow": follow}))[0]

    serializer = serializers.AcceptFollowSerializer(
        follow, context={"actor": follow.target.actor}
    )
    expected = serializer.data
    expected["to"] = [follow.actor]

    assert activity["payload"] == expected
    assert activity["actor"] == follow.target.actor
    assert activity["object"] == follow


def test_inbox_accept(factories, mocker):
    mocked_scan = mocker.patch("funkwhale_api.music.models.Library.schedule_scan")
    local_actor = factories["users.User"]().create_actor()
    remote_actor = factories["federation.Actor"]()
    follow = factories["federation.LibraryFollow"](
        actor=local_actor, target__actor=remote_actor
    )
    assert follow.approved is None
    serializer = serializers.AcceptFollowSerializer(
        follow, context={"actor": remote_actor}
    )
    ii = factories["federation.InboxItem"](actor=local_actor)
    result = routes.inbox_accept(
        serializer.data,
        context={"actor": remote_actor, "inbox_items": [ii], "raise_exception": True},
    )
    assert result["object"] == follow
    assert result["related_object"] == follow.target

    follow.refresh_from_db()

    assert follow.approved is True
    mocked_scan.assert_called_once_with()


def test_outbox_follow_library(factories, mocker):
    follow = factories["federation.LibraryFollow"]()
    activity = list(routes.outbox_follow({"follow": follow}))[0]
    serializer = serializers.FollowSerializer(follow, context={"actor": follow.actor})
    expected = serializer.data
    expected["to"] = [follow.target.actor]

    assert activity["payload"] == expected
    assert activity["actor"] == follow.actor
    assert activity["object"] == follow.target
