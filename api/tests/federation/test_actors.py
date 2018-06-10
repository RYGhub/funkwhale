import arrow
import pytest

from django.urls import reverse
from django.utils import timezone

from rest_framework import exceptions

from funkwhale_api.federation import actors
from funkwhale_api.federation import models
from funkwhale_api.federation import serializers
from funkwhale_api.federation import utils
from funkwhale_api.music import models as music_models
from funkwhale_api.music import tasks as music_tasks


def test_actor_fetching(r_mock):
    payload = {
        "id": "https://actor.mock/users/actor#main-key",
        "owner": "test",
        "publicKeyPem": "test_pem",
    }
    actor_url = "https://actor.mock/"
    r_mock.get(actor_url, json=payload)
    r = actors.get_actor_data(actor_url)

    assert r == payload


def test_get_actor(factories, r_mock):
    actor = factories["federation.Actor"].build()
    payload = serializers.ActorSerializer(actor).data
    r_mock.get(actor.url, json=payload)
    new_actor = actors.get_actor(actor.url)

    assert new_actor.pk is not None
    assert serializers.ActorSerializer(new_actor).data == payload


def test_get_actor_use_existing(factories, preferences, mocker):
    preferences["federation__actor_fetch_delay"] = 60
    actor = factories["federation.Actor"]()
    get_data = mocker.patch("funkwhale_api.federation.actors.get_actor_data")
    new_actor = actors.get_actor(actor.url)

    assert new_actor == actor
    get_data.assert_not_called()


def test_get_actor_refresh(factories, preferences, mocker):
    preferences["federation__actor_fetch_delay"] = 0
    actor = factories["federation.Actor"]()
    payload = serializers.ActorSerializer(actor).data
    # actor changed their username in the meantime
    payload["preferredUsername"] = "New me"
    get_data = mocker.patch(
        "funkwhale_api.federation.actors.get_actor_data", return_value=payload
    )
    new_actor = actors.get_actor(actor.url)

    assert new_actor == actor
    assert new_actor.last_fetch_date > actor.last_fetch_date
    assert new_actor.preferred_username == "New me"


def test_get_library(db, settings, mocker):
    get_key_pair = mocker.patch(
        "funkwhale_api.federation.keys.get_key_pair",
        return_value=(b"private", b"public"),
    )
    expected = {
        "preferred_username": "library",
        "domain": settings.FEDERATION_HOSTNAME,
        "type": "Person",
        "name": "{}'s library".format(settings.FEDERATION_HOSTNAME),
        "manually_approves_followers": True,
        "public_key": "public",
        "url": utils.full_url(
            reverse("federation:instance-actors-detail", kwargs={"actor": "library"})
        ),
        "shared_inbox_url": utils.full_url(
            reverse("federation:instance-actors-inbox", kwargs={"actor": "library"})
        ),
        "inbox_url": utils.full_url(
            reverse("federation:instance-actors-inbox", kwargs={"actor": "library"})
        ),
        "outbox_url": utils.full_url(
            reverse("federation:instance-actors-outbox", kwargs={"actor": "library"})
        ),
        "summary": "Bot account to federate with {}'s library".format(
            settings.FEDERATION_HOSTNAME
        ),
    }
    actor = actors.SYSTEM_ACTORS["library"].get_actor_instance()
    for key, value in expected.items():
        assert getattr(actor, key) == value


def test_get_test(db, mocker, settings):
    get_key_pair = mocker.patch(
        "funkwhale_api.federation.keys.get_key_pair",
        return_value=(b"private", b"public"),
    )
    expected = {
        "preferred_username": "test",
        "domain": settings.FEDERATION_HOSTNAME,
        "type": "Person",
        "name": "{}'s test account".format(settings.FEDERATION_HOSTNAME),
        "manually_approves_followers": False,
        "public_key": "public",
        "url": utils.full_url(
            reverse("federation:instance-actors-detail", kwargs={"actor": "test"})
        ),
        "shared_inbox_url": utils.full_url(
            reverse("federation:instance-actors-inbox", kwargs={"actor": "test"})
        ),
        "inbox_url": utils.full_url(
            reverse("federation:instance-actors-inbox", kwargs={"actor": "test"})
        ),
        "outbox_url": utils.full_url(
            reverse("federation:instance-actors-outbox", kwargs={"actor": "test"})
        ),
        "summary": "Bot account to test federation with {}. Send me /ping and I'll answer you.".format(
            settings.FEDERATION_HOSTNAME
        ),
    }
    actor = actors.SYSTEM_ACTORS["test"].get_actor_instance()
    for key, value in expected.items():
        assert getattr(actor, key) == value


def test_test_get_outbox():
    expected = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
            {},
        ],
        "id": utils.full_url(
            reverse("federation:instance-actors-outbox", kwargs={"actor": "test"})
        ),
        "type": "OrderedCollection",
        "totalItems": 0,
        "orderedItems": [],
    }

    data = actors.SYSTEM_ACTORS["test"].get_outbox({}, actor=None)

    assert data == expected


def test_test_post_inbox_requires_authenticated_actor():
    with pytest.raises(exceptions.PermissionDenied):
        actors.SYSTEM_ACTORS["test"].post_inbox({}, actor=None)


def test_test_post_outbox_validates_actor(nodb_factories):
    actor = nodb_factories["federation.Actor"]()
    data = {"actor": "noop"}
    with pytest.raises(exceptions.ValidationError) as exc_info:
        actors.SYSTEM_ACTORS["test"].post_inbox(data, actor=actor)
        msg = "The actor making the request do not match"
        assert msg in exc_info.value


def test_test_post_inbox_handles_create_note(settings, mocker, factories):
    deliver = mocker.patch("funkwhale_api.federation.activity.deliver")
    actor = factories["federation.Actor"]()
    now = timezone.now()
    mocker.patch("django.utils.timezone.now", return_value=now)
    data = {
        "actor": actor.url,
        "type": "Create",
        "id": "http://test.federation/activity",
        "object": {
            "type": "Note",
            "id": "http://test.federation/object",
            "content": "<p><a>@mention</a> /ping</p>",
        },
    }
    test_actor = actors.SYSTEM_ACTORS["test"].get_actor_instance()
    expected_note = factories["federation.Note"](
        id="https://test.federation/activities/note/{}".format(now.timestamp()),
        content="Pong!",
        published=now.isoformat(),
        inReplyTo=data["object"]["id"],
        cc=[],
        summary=None,
        sensitive=False,
        attributedTo=test_actor.url,
        attachment=[],
        to=[actor.url],
        url="https://{}/activities/note/{}".format(
            settings.FEDERATION_HOSTNAME, now.timestamp()
        ),
        tag=[{"href": actor.url, "name": actor.mention_username, "type": "Mention"}],
    )
    expected_activity = {
        "@context": serializers.AP_CONTEXT,
        "actor": test_actor.url,
        "id": "https://{}/activities/note/{}/activity".format(
            settings.FEDERATION_HOSTNAME, now.timestamp()
        ),
        "to": actor.url,
        "type": "Create",
        "published": now.isoformat(),
        "object": expected_note,
        "cc": [],
    }
    actors.SYSTEM_ACTORS["test"].post_inbox(data, actor=actor)
    deliver.assert_called_once_with(
        expected_activity,
        to=[actor.url],
        on_behalf_of=actors.SYSTEM_ACTORS["test"].get_actor_instance(),
    )


def test_getting_actor_instance_persists_in_db(db):
    test = actors.SYSTEM_ACTORS["test"].get_actor_instance()
    from_db = models.Actor.objects.get(url=test.url)

    for f in test._meta.fields:
        assert getattr(from_db, f.name) == getattr(test, f.name)


@pytest.mark.parametrize(
    "username,domain,expected",
    [("test", "wrongdomain.com", False), ("notsystem", "", False), ("test", "", True)],
)
def test_actor_is_system(username, domain, expected, nodb_factories, settings):
    if not domain:
        domain = settings.FEDERATION_HOSTNAME

    actor = nodb_factories["federation.Actor"](
        preferred_username=username, domain=domain
    )
    assert actor.is_system is expected


@pytest.mark.parametrize(
    "username,domain,expected",
    [
        ("test", "wrongdomain.com", None),
        ("notsystem", "", None),
        ("test", "", actors.SYSTEM_ACTORS["test"]),
    ],
)
def test_actor_is_system(username, domain, expected, nodb_factories, settings):
    if not domain:
        domain = settings.FEDERATION_HOSTNAME
    actor = nodb_factories["federation.Actor"](
        preferred_username=username, domain=domain
    )
    assert actor.system_conf == expected


@pytest.mark.parametrize("value", [False, True])
def test_library_actor_manually_approves_based_on_preference(value, preferences):
    preferences["federation__music_needs_approval"] = value
    library_conf = actors.SYSTEM_ACTORS["library"]
    assert library_conf.manually_approves_followers is value


def test_system_actor_handle(mocker, nodb_factories):
    handler = mocker.patch("funkwhale_api.federation.actors.TestActor.handle_create")
    actor = nodb_factories["federation.Actor"]()
    activity = nodb_factories["federation.Activity"](type="Create", actor=actor.url)
    serializer = serializers.ActivitySerializer(data=activity)
    assert serializer.is_valid()
    actors.SYSTEM_ACTORS["test"].handle(activity, actor)
    handler.assert_called_once_with(activity, actor)


def test_test_actor_handles_follow(settings, mocker, factories):
    deliver = mocker.patch("funkwhale_api.federation.activity.deliver")
    actor = factories["federation.Actor"]()
    accept_follow = mocker.patch("funkwhale_api.federation.activity.accept_follow")
    test_actor = actors.SYSTEM_ACTORS["test"].get_actor_instance()
    data = {
        "actor": actor.url,
        "type": "Follow",
        "id": "http://test.federation/user#follows/267",
        "object": test_actor.url,
    }
    actors.SYSTEM_ACTORS["test"].post_inbox(data, actor=actor)
    follow = models.Follow.objects.get(target=test_actor, approved=True)
    follow_back = models.Follow.objects.get(actor=test_actor, approved=None)
    accept_follow.assert_called_once_with(follow)
    deliver.assert_called_once_with(
        serializers.FollowSerializer(follow_back).data,
        on_behalf_of=test_actor,
        to=[actor.url],
    )


def test_test_actor_handles_undo_follow(settings, mocker, factories):
    deliver = mocker.patch("funkwhale_api.federation.activity.deliver")
    test_actor = actors.SYSTEM_ACTORS["test"].get_actor_instance()
    follow = factories["federation.Follow"](target=test_actor)
    reverse_follow = factories["federation.Follow"](
        actor=test_actor, target=follow.actor
    )
    follow_serializer = serializers.FollowSerializer(follow)
    reverse_follow_serializer = serializers.FollowSerializer(reverse_follow)
    undo = {
        "@context": serializers.AP_CONTEXT,
        "type": "Undo",
        "id": follow_serializer.data["id"] + "/undo",
        "actor": follow.actor.url,
        "object": follow_serializer.data,
    }
    expected_undo = {
        "@context": serializers.AP_CONTEXT,
        "type": "Undo",
        "id": reverse_follow_serializer.data["id"] + "/undo",
        "actor": reverse_follow.actor.url,
        "object": reverse_follow_serializer.data,
    }

    actors.SYSTEM_ACTORS["test"].post_inbox(undo, actor=follow.actor)
    deliver.assert_called_once_with(
        expected_undo, to=[follow.actor.url], on_behalf_of=test_actor
    )

    assert models.Follow.objects.count() == 0


def test_library_actor_handles_follow_manual_approval(preferences, mocker, factories):
    preferences["federation__music_needs_approval"] = True
    actor = factories["federation.Actor"]()
    now = timezone.now()
    mocker.patch("django.utils.timezone.now", return_value=now)
    library_actor = actors.SYSTEM_ACTORS["library"].get_actor_instance()
    data = {
        "actor": actor.url,
        "type": "Follow",
        "id": "http://test.federation/user#follows/267",
        "object": library_actor.url,
    }

    library_actor.system_conf.post_inbox(data, actor=actor)
    follow = library_actor.received_follows.first()

    assert follow.actor == actor
    assert follow.approved is None


def test_library_actor_handles_follow_auto_approval(preferences, mocker, factories):
    preferences["federation__music_needs_approval"] = False
    actor = factories["federation.Actor"]()
    mocker.patch("funkwhale_api.federation.activity.accept_follow")
    library_actor = actors.SYSTEM_ACTORS["library"].get_actor_instance()
    data = {
        "actor": actor.url,
        "type": "Follow",
        "id": "http://test.federation/user#follows/267",
        "object": library_actor.url,
    }
    library_actor.system_conf.post_inbox(data, actor=actor)

    follow = library_actor.received_follows.first()

    assert follow.actor == actor
    assert follow.approved is True


def test_library_actor_handles_accept(mocker, factories):
    library_actor = actors.SYSTEM_ACTORS["library"].get_actor_instance()
    actor = factories["federation.Actor"]()
    pending_follow = factories["federation.Follow"](
        actor=library_actor, target=actor, approved=None
    )
    serializer = serializers.AcceptFollowSerializer(pending_follow)
    library_actor.system_conf.post_inbox(serializer.data, actor=actor)

    pending_follow.refresh_from_db()

    assert pending_follow.approved is True


def test_library_actor_handle_create_audio_no_library(mocker, factories):
    # when we receive inbox create audio, we should not do anything
    # if we don't have a configured library matching the sender
    mocked_create = mocker.patch(
        "funkwhale_api.federation.serializers.AudioSerializer.create"
    )
    actor = factories["federation.Actor"]()
    library_actor = actors.SYSTEM_ACTORS["library"].get_actor_instance()
    data = {
        "actor": actor.url,
        "type": "Create",
        "id": "http://test.federation/audio/create",
        "object": {
            "id": "https://batch.import",
            "type": "Collection",
            "totalItems": 2,
            "items": factories["federation.Audio"].create_batch(size=2),
        },
    }
    library_actor.system_conf.post_inbox(data, actor=actor)

    mocked_create.assert_not_called()
    models.LibraryTrack.objects.count() == 0


def test_library_actor_handle_create_audio_no_library_enabled(mocker, factories):
    # when we receive inbox create audio, we should not do anything
    # if we don't have an enabled library
    mocked_create = mocker.patch(
        "funkwhale_api.federation.serializers.AudioSerializer.create"
    )
    disabled_library = factories["federation.Library"](federation_enabled=False)
    actor = disabled_library.actor
    library_actor = actors.SYSTEM_ACTORS["library"].get_actor_instance()
    data = {
        "actor": actor.url,
        "type": "Create",
        "id": "http://test.federation/audio/create",
        "object": {
            "id": "https://batch.import",
            "type": "Collection",
            "totalItems": 2,
            "items": factories["federation.Audio"].create_batch(size=2),
        },
    }
    library_actor.system_conf.post_inbox(data, actor=actor)

    mocked_create.assert_not_called()
    models.LibraryTrack.objects.count() == 0


def test_library_actor_handle_create_audio(mocker, factories):
    library_actor = actors.SYSTEM_ACTORS["library"].get_actor_instance()
    remote_library = factories["federation.Library"](federation_enabled=True)

    data = {
        "actor": remote_library.actor.url,
        "type": "Create",
        "id": "http://test.federation/audio/create",
        "object": {
            "id": "https://batch.import",
            "type": "Collection",
            "totalItems": 2,
            "items": factories["federation.Audio"].create_batch(size=2),
        },
    }

    library_actor.system_conf.post_inbox(data, actor=remote_library.actor)

    lts = list(remote_library.tracks.order_by("id"))

    assert len(lts) == 2

    for i, a in enumerate(data["object"]["items"]):
        lt = lts[i]
        assert lt.pk is not None
        assert lt.url == a["id"]
        assert lt.library == remote_library
        assert lt.audio_url == a["url"]["href"]
        assert lt.audio_mimetype == a["url"]["mediaType"]
        assert lt.metadata == a["metadata"]
        assert lt.title == a["metadata"]["recording"]["title"]
        assert lt.artist_name == a["metadata"]["artist"]["name"]
        assert lt.album_title == a["metadata"]["release"]["title"]
        assert lt.published_date == arrow.get(a["published"])


def test_library_actor_handle_create_audio_autoimport(mocker, factories):
    mocked_import = mocker.patch("funkwhale_api.common.utils.on_commit")
    library_actor = actors.SYSTEM_ACTORS["library"].get_actor_instance()
    remote_library = factories["federation.Library"](
        federation_enabled=True, autoimport=True
    )

    data = {
        "actor": remote_library.actor.url,
        "type": "Create",
        "id": "http://test.federation/audio/create",
        "object": {
            "id": "https://batch.import",
            "type": "Collection",
            "totalItems": 2,
            "items": factories["federation.Audio"].create_batch(size=2),
        },
    }

    library_actor.system_conf.post_inbox(data, actor=remote_library.actor)

    lts = list(remote_library.tracks.order_by("id"))

    assert len(lts) == 2

    for i, a in enumerate(data["object"]["items"]):
        lt = lts[i]
        assert lt.pk is not None
        assert lt.url == a["id"]
        assert lt.library == remote_library
        assert lt.audio_url == a["url"]["href"]
        assert lt.audio_mimetype == a["url"]["mediaType"]
        assert lt.metadata == a["metadata"]
        assert lt.title == a["metadata"]["recording"]["title"]
        assert lt.artist_name == a["metadata"]["artist"]["name"]
        assert lt.album_title == a["metadata"]["release"]["title"]
        assert lt.published_date == arrow.get(a["published"])

    batch = music_models.ImportBatch.objects.latest("id")

    assert batch.jobs.count() == len(lts)
    assert batch.source == "federation"
    assert batch.submitted_by is None

    for i, job in enumerate(batch.jobs.order_by("id")):
        lt = lts[i]
        assert job.library_track == lt
        assert job.mbid == lt.mbid
        assert job.source == lt.url

        mocked_import.assert_any_call(
            music_tasks.import_job_run.delay, import_job_id=job.pk, use_acoustid=False
        )
