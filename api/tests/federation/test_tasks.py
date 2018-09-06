import datetime
import os
import pathlib
import pytest

from django.utils import timezone

from funkwhale_api.federation import tasks


def test_clean_federation_music_cache_if_no_listen(preferences, factories):
    preferences["federation__music_cache_duration"] = 60
    remote_library = factories["music.Library"]()
    tf1 = factories["music.TrackFile"](
        library=remote_library, accessed_date=timezone.now()
    )
    tf2 = factories["music.TrackFile"](
        library=remote_library,
        accessed_date=timezone.now() - datetime.timedelta(minutes=61),
    )
    tf3 = factories["music.TrackFile"](library=remote_library, accessed_date=None)
    path1 = tf1.audio_file.path
    path2 = tf2.audio_file.path
    path3 = tf3.audio_file.path

    tasks.clean_music_cache()

    tf1.refresh_from_db()
    tf2.refresh_from_db()
    tf3.refresh_from_db()

    assert bool(tf1.audio_file) is True
    assert bool(tf2.audio_file) is False
    assert bool(tf3.audio_file) is False
    assert os.path.exists(path1) is True
    assert os.path.exists(path2) is False
    assert os.path.exists(path3) is False


def test_clean_federation_music_cache_orphaned(settings, preferences, factories):
    preferences["federation__music_cache_duration"] = 60
    path = os.path.join(settings.MEDIA_ROOT, "federation_cache", "tracks")
    keep_path = os.path.join(os.path.join(path, "1a", "b2"), "keep.ogg")
    remove_path = os.path.join(os.path.join(path, "c3", "d4"), "remove.ogg")
    os.makedirs(os.path.dirname(keep_path), exist_ok=True)
    os.makedirs(os.path.dirname(remove_path), exist_ok=True)
    pathlib.Path(keep_path).touch()
    pathlib.Path(remove_path).touch()
    tf = factories["music.TrackFile"](
        accessed_date=timezone.now(), audio_file__path=keep_path
    )

    tasks.clean_music_cache()

    tf.refresh_from_db()

    assert bool(tf.audio_file) is True
    assert os.path.exists(tf.audio_file.path) is True
    assert os.path.exists(remove_path) is False


def test_handle_in(factories, mocker, now):
    mocked_dispatch = mocker.patch("funkwhale_api.federation.routes.inbox.dispatch")

    r1 = factories["users.User"](with_actor=True).actor
    r2 = factories["users.User"](with_actor=True).actor
    a = factories["federation.Activity"](payload={"hello": "world"})
    ii1 = factories["federation.InboxItem"](activity=a, actor=r1)
    ii2 = factories["federation.InboxItem"](activity=a, actor=r2)
    tasks.dispatch_inbox(activity_id=a.pk)

    mocked_dispatch.assert_called_once_with(
        a.payload, context={"actor": a.actor, "inbox_items": [ii1, ii2]}
    )

    ii1.refresh_from_db()
    ii2.refresh_from_db()

    assert ii1.is_delivered is True
    assert ii2.is_delivered is True
    assert ii1.last_delivery_date == now
    assert ii2.last_delivery_date == now


def test_handle_in_error(factories, mocker, now):
    mocker.patch(
        "funkwhale_api.federation.routes.inbox.dispatch", side_effect=Exception()
    )
    r1 = factories["users.User"](with_actor=True).actor
    r2 = factories["users.User"](with_actor=True).actor

    a = factories["federation.Activity"](payload={"hello": "world"})
    factories["federation.InboxItem"](activity=a, actor=r1)
    factories["federation.InboxItem"](activity=a, actor=r2)

    with pytest.raises(Exception):
        tasks.dispatch_inbox(activity_id=a.pk)

    assert a.inbox_items.filter(is_delivered=False).count() == 2


def test_dispatch_outbox_to_inbox(factories, mocker):
    mocked_inbox = mocker.patch("funkwhale_api.federation.tasks.dispatch_inbox.delay")
    mocked_deliver_to_remote_inbox = mocker.patch(
        "funkwhale_api.federation.tasks.deliver_to_remote_inbox.delay"
    )
    activity = factories["federation.Activity"](actor__local=True)
    factories["federation.InboxItem"](activity=activity, actor__local=True)
    remote_ii = factories["federation.InboxItem"](
        activity=activity,
        actor__shared_inbox_url=None,
        actor__inbox_url="https://test.inbox",
    )
    tasks.dispatch_outbox(activity_id=activity.pk)
    mocked_inbox.assert_called_once_with(activity_id=activity.pk)
    mocked_deliver_to_remote_inbox.assert_called_once_with(
        activity_id=activity.pk, inbox_url=remote_ii.actor.inbox_url
    )


def test_dispatch_outbox_to_shared_inbox_url(factories, mocker):
    mocked_deliver_to_remote_inbox = mocker.patch(
        "funkwhale_api.federation.tasks.deliver_to_remote_inbox.delay"
    )
    activity = factories["federation.Activity"](actor__local=True)
    # shared inbox
    remote_ii_shared1 = factories["federation.InboxItem"](
        activity=activity, actor__shared_inbox_url="https://shared.inbox"
    )
    # another on the same shared inbox
    factories["federation.InboxItem"](
        activity=activity, actor__shared_inbox_url="https://shared.inbox"
    )
    # one on a dedicated inbox
    remote_ii_single = factories["federation.InboxItem"](
        activity=activity,
        actor__shared_inbox_url=None,
        actor__inbox_url="https://single.inbox",
    )
    tasks.dispatch_outbox(activity_id=activity.pk)

    assert mocked_deliver_to_remote_inbox.call_count == 2
    mocked_deliver_to_remote_inbox.assert_any_call(
        activity_id=activity.pk,
        shared_inbox_url=remote_ii_shared1.actor.shared_inbox_url,
    )
    mocked_deliver_to_remote_inbox.assert_any_call(
        activity_id=activity.pk, inbox_url=remote_ii_single.actor.inbox_url
    )


def test_deliver_to_remote_inbox_inbox_url(factories, r_mock):
    activity = factories["federation.Activity"]()
    url = "https://test.shared/"
    r_mock.post(url)

    tasks.deliver_to_remote_inbox(activity_id=activity.pk, inbox_url=url)

    request = r_mock.request_history[0]

    assert r_mock.called is True
    assert r_mock.call_count == 1
    assert request.url == url
    assert request.headers["content-type"] == "application/activity+json"
    assert request.json() == activity.payload


def test_deliver_to_remote_inbox_shared_inbox_url(factories, r_mock):
    activity = factories["federation.Activity"]()
    url = "https://test.shared/"
    r_mock.post(url)

    tasks.deliver_to_remote_inbox(activity_id=activity.pk, shared_inbox_url=url)

    request = r_mock.request_history[0]

    assert r_mock.called is True
    assert r_mock.call_count == 1
    assert request.url == url
    assert request.headers["content-type"] == "application/activity+json"
    assert request.json() == activity.payload


def test_deliver_to_remote_inbox_success_shared_inbox_marks_inbox_items_as_delivered(
    factories, r_mock, now
):
    activity = factories["federation.Activity"]()
    url = "https://test.shared/"
    r_mock.post(url)
    ii = factories["federation.InboxItem"](
        activity=activity, actor__shared_inbox_url=url
    )
    other_ii = factories["federation.InboxItem"](
        activity=activity, actor__shared_inbox_url="https://other.url"
    )
    tasks.deliver_to_remote_inbox(activity_id=activity.pk, shared_inbox_url=url)

    ii.refresh_from_db()
    other_ii.refresh_from_db()

    assert ii.is_delivered is True
    assert ii.last_delivery_date == now
    assert other_ii.is_delivered is False
    assert other_ii.last_delivery_date is None


def test_deliver_to_remote_inbox_success_single_inbox_marks_inbox_items_as_delivered(
    factories, r_mock, now
):
    activity = factories["federation.Activity"]()
    url = "https://test.single/"
    r_mock.post(url)
    ii = factories["federation.InboxItem"](activity=activity, actor__inbox_url=url)
    other_ii = factories["federation.InboxItem"](
        activity=activity, actor__inbox_url="https://other.url"
    )
    tasks.deliver_to_remote_inbox(activity_id=activity.pk, inbox_url=url)

    ii.refresh_from_db()
    other_ii.refresh_from_db()

    assert ii.is_delivered is True
    assert ii.last_delivery_date == now
    assert other_ii.is_delivered is False
    assert other_ii.last_delivery_date is None


def test_deliver_to_remote_inbox_error(factories, r_mock, now):
    activity = factories["federation.Activity"]()
    url = "https://test.single/"
    r_mock.post(url, status_code=404)
    ii = factories["federation.InboxItem"](activity=activity, actor__inbox_url=url)
    with pytest.raises(tasks.RequestException):
        tasks.deliver_to_remote_inbox(activity_id=activity.pk, inbox_url=url)

    ii.refresh_from_db()

    assert ii.is_delivered is False
    assert ii.last_delivery_date == now
    assert ii.delivery_attempts == 1
