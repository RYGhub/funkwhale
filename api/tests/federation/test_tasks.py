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
    # local upload, should not be cleaned
    upload4 = factories["music.Upload"](library__actor__local=True, accessed_date=None)

    path1 = upload1.audio_file.path
    path2 = upload2.audio_file.path
    path3 = upload3.audio_file.path
    path4 = upload4.audio_file.path

    tasks.clean_music_cache()

    upload1.refresh_from_db()
    upload2.refresh_from_db()
    upload3.refresh_from_db()
    upload4.refresh_from_db()

    assert bool(upload1.audio_file) is True
    assert bool(upload2.audio_file) is False
    assert bool(upload3.audio_file) is False
    assert bool(upload4.audio_file) is True
    assert os.path.exists(path1) is True
    assert os.path.exists(path2) is False
    assert os.path.exists(path3) is False
    assert os.path.exists(path4) is True


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


def test_fetch_nodeinfo(factories, r_mock, now):
    wellknown_url = "https://test.test/.well-known/nodeinfo"
    nodeinfo_url = "https://test.test/nodeinfo"

    r_mock.get(
        wellknown_url,
        json={
            "links": [
                {
                    "rel": "http://nodeinfo.diaspora.software/ns/schema/2.0",
                    "href": "https://test.test/nodeinfo",
                }
            ]
        },
    )
    r_mock.get(nodeinfo_url, json={"hello": "world"})

    assert tasks.fetch_nodeinfo("test.test") == {"hello": "world"}


def test_update_domain_nodeinfo(factories, mocker, now):
    domain = factories["federation.Domain"]()
    mocker.patch.object(tasks, "fetch_nodeinfo", return_value={"hello": "world"})

    assert domain.nodeinfo == {}
    assert domain.nodeinfo_fetch_date is None

    tasks.update_domain_nodeinfo(domain_name=domain.name)

    domain.refresh_from_db()

    assert domain.nodeinfo_fetch_date == now
    assert domain.nodeinfo == {"status": "ok", "payload": {"hello": "world"}}


def test_update_domain_nodeinfo_error(factories, r_mock, now):
    domain = factories["federation.Domain"]()
    wellknown_url = "https://{}/.well-known/nodeinfo".format(domain.name)

    r_mock.get(wellknown_url, status_code=500)

    tasks.update_domain_nodeinfo(domain_name=domain.name)

    domain.refresh_from_db()

    assert domain.nodeinfo_fetch_date == now
    assert domain.nodeinfo == {
        "status": "error",
        "error": "500 Server Error: None for url: {}".format(wellknown_url),
    }


def test_handle_purge_actors(factories, mocker):
    to_purge = factories["federation.Actor"]()
    keeped = [
        factories["music.Upload"](),
        factories["federation.Activity"](),
        factories["federation.InboxItem"](),
        factories["federation.Follow"](),
        factories["federation.LibraryFollow"](),
    ]

    library = factories["music.Library"](actor=to_purge)
    deleted = [
        library,
        factories["music.Upload"](library=library),
        factories["federation.Activity"](actor=to_purge),
        factories["federation.InboxItem"](actor=to_purge),
        factories["federation.Follow"](actor=to_purge),
        factories["federation.LibraryFollow"](actor=to_purge),
    ]

    tasks.handle_purge_actors([to_purge.pk])

    for k in keeped:
        # this should not be deleted
        k.refresh_from_db()

    for d in deleted:
        with pytest.raises(d.__class__.DoesNotExist):
            d.refresh_from_db()


def test_purge_actors(factories, mocker):
    handle_purge_actors = mocker.spy(tasks, "handle_purge_actors")
    factories["federation.Actor"]()
    to_delete = factories["federation.Actor"]()
    to_delete_domain = factories["federation.Actor"]()
    tasks.purge_actors(ids=[to_delete.pk], domains=[to_delete_domain.domain.name])

    handle_purge_actors.assert_called_once_with(ids=[to_delete.pk, to_delete_domain.pk])
