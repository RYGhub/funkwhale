import datetime
import os
import pathlib
import pytest

from django.utils import timezone

from funkwhale_api.federation import tasks


def test_clean_federation_music_cache_if_no_listen(preferences, factories):
    preferences["federation__music_cache_duration"] = 60
    remote_library = factories["music.Library"]()
    upload1 = factories["music.Upload"](
        library=remote_library, accessed_date=timezone.now()
    )
    upload2 = factories["music.Upload"](
        library=remote_library,
        accessed_date=timezone.now() - datetime.timedelta(minutes=61),
    )
    upload3 = factories["music.Upload"](library=remote_library, accessed_date=None)
    path1 = upload1.audio_file.path
    path2 = upload2.audio_file.path
    path3 = upload3.audio_file.path

    tasks.clean_music_cache()

    upload1.refresh_from_db()
    upload2.refresh_from_db()
    upload3.refresh_from_db()

    assert bool(upload1.audio_file) is True
    assert bool(upload2.audio_file) is False
    assert bool(upload3.audio_file) is False
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
    upload = factories["music.Upload"](
        accessed_date=timezone.now(), audio_file__path=keep_path
    )

    tasks.clean_music_cache()

    upload.refresh_from_db()

    assert bool(upload.audio_file) is True
    assert os.path.exists(upload.audio_file.path) is True
    assert os.path.exists(remove_path) is False


def test_handle_in(factories, mocker, now, queryset_equal_list):
    mocked_dispatch = mocker.patch("funkwhale_api.federation.routes.inbox.dispatch")

    r1 = factories["users.User"](with_actor=True).actor
    r2 = factories["users.User"](with_actor=True).actor
    a = factories["federation.Activity"](payload={"hello": "world"})
    ii1 = factories["federation.InboxItem"](activity=a, actor=r1)
    ii2 = factories["federation.InboxItem"](activity=a, actor=r2)
    tasks.dispatch_inbox(activity_id=a.pk)

    mocked_dispatch.assert_called_once_with(
        a.payload, context={"actor": a.actor, "activity": a, "inbox_items": [ii1, ii2]}
    )


def test_dispatch_outbox(factories, mocker):
    mocked_inbox = mocker.patch("funkwhale_api.federation.tasks.dispatch_inbox.delay")
    mocked_deliver_to_remote = mocker.patch(
        "funkwhale_api.federation.tasks.deliver_to_remote.delay"
    )
    activity = factories["federation.Activity"](actor__local=True)
    factories["federation.InboxItem"](activity=activity)
    delivery = factories["federation.Delivery"](activity=activity)
    tasks.dispatch_outbox(activity_id=activity.pk)
    mocked_inbox.assert_called_once_with(activity_id=activity.pk)
    mocked_deliver_to_remote.assert_called_once_with(delivery_id=delivery.pk)


def test_dispatch_outbox_disabled_federation(factories, mocker, preferences):
    preferences["federation__enabled"] = False
    mocked_inbox = mocker.patch("funkwhale_api.federation.tasks.dispatch_inbox.delay")
    mocked_deliver_to_remote = mocker.patch(
        "funkwhale_api.federation.tasks.deliver_to_remote.delay"
    )
    activity = factories["federation.Activity"](actor__local=True)
    factories["federation.InboxItem"](activity=activity)
    factories["federation.Delivery"](activity=activity)
    tasks.dispatch_outbox(activity_id=activity.pk)
    mocked_inbox.assert_called_once_with(activity_id=activity.pk)
    mocked_deliver_to_remote.assert_not_called()


def test_deliver_to_remote_success_mark_as_delivered(factories, r_mock, now):
    delivery = factories["federation.Delivery"]()
    r_mock.post(delivery.inbox_url)
    tasks.deliver_to_remote(delivery_id=delivery.pk)

    delivery.refresh_from_db()

    request = r_mock.request_history[0]
    assert delivery.is_delivered is True
    assert delivery.attempts == 1
    assert delivery.last_attempt_date == now
    assert r_mock.called is True
    assert r_mock.call_count == 1
    assert request.url == delivery.inbox_url
    assert request.headers["content-type"] == "application/activity+json"
    assert request.json() == delivery.activity.payload


def test_deliver_to_remote_error(factories, r_mock, now):
    delivery = factories["federation.Delivery"]()
    r_mock.post(delivery.inbox_url, status_code=404)

    with pytest.raises(tasks.RequestException):
        tasks.deliver_to_remote(delivery_id=delivery.pk)

    delivery.refresh_from_db()

    assert delivery.is_delivered is False
    assert delivery.attempts == 1
    assert delivery.last_attempt_date == now
