import pytest
from django import db

from funkwhale_api.federation import models
from funkwhale_api.music import models as music_models


def test_cannot_duplicate_actor(factories):
    actor = factories["federation.Actor"]()

    with pytest.raises(db.IntegrityError):
        factories["federation.Actor"](
            domain=actor.domain, preferred_username=actor.preferred_username
        )


def test_cannot_duplicate_follow(factories):
    follow = factories["federation.Follow"]()

    with pytest.raises(db.IntegrityError):
        factories["federation.Follow"](target=follow.target, actor=follow.actor)


def test_follow_federation_url(factories):
    follow = factories["federation.Follow"](local=True)
    expected = "{}#follows/{}".format(follow.actor.fid, follow.uuid)

    assert follow.get_federation_id() == expected


def test_actor_get_quota(factories):
    library = factories["music.Library"]()
    factories["music.Upload"](
        library=library,
        import_status="pending",
        audio_file__from_path=None,
        audio_file__data=b"a",
    )
    factories["music.Upload"](
        library=library,
        import_status="skipped",
        audio_file__from_path=None,
        audio_file__data=b"aa",
    )
    factories["music.Upload"](
        library=library,
        import_status="errored",
        audio_file__from_path=None,
        audio_file__data=b"aaa",
    )
    factories["music.Upload"](
        library=library,
        import_status="finished",
        audio_file__from_path=None,
        audio_file__data=b"aaaa",
    )
    factories["music.Upload"](
        library=library,
        import_status="draft",
        audio_file__from_path=None,
        audio_file__data=b"aaaaa",
    )

    # this one is imported in place and don't count
    factories["music.Upload"](
        library=library,
        import_status="finished",
        source="file://test",
        audio_file=None,
        size=42,
    )
    # this one is imported in place but count because there is a mapped file
    factories["music.Upload"](
        library=library,
        import_status="finished",
        source="file://test2",
        audio_file__from_path=None,
        audio_file__data=b"aaaa",
    )

    # this one is in a channel
    channel = factories["audio.Channel"](attributed_to=library.actor)
    factories["music.Upload"](
        library=channel.library,
        import_status="finished",
        audio_file__from_path=None,
        audio_file__data=b"aaaaa",
    )

    expected = {
        "total": 24,
        "pending": 1,
        "skipped": 2,
        "errored": 3,
        "finished": 13,
        "draft": 5,
    }

    assert library.actor.get_current_usage() == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("Domain.com", "domain.com"),
        ("hello-WORLD.com", "hello-world.com"),
        ("posés.com", "posés.com"),
    ],
)
def test_domain_name_saved_properly(value, expected, factories):
    domain = factories["federation.Domain"](name=value)
    assert domain.name == expected


def test_external_domains(factories, settings):
    d1 = factories["federation.Domain"]()
    d2 = factories["federation.Domain"]()
    settings.FEDERATION_HOSTNAME = d1.pk

    assert list(models.Domain.objects.external()) == [d2]


def test_domain_stats(factories):
    expected = {
        "actors": 0,
        "libraries": 0,
        "tracks": 0,
        "albums": 0,
        "channels": 0,
        "uploads": 0,
        "artists": 0,
        "outbox_activities": 0,
        "received_library_follows": 0,
        "emitted_library_follows": 0,
        "media_total_size": 0,
        "media_downloaded_size": 0,
    }

    domain = factories["federation.Domain"]()

    assert domain.get_stats() == expected


def test_actor_stats(factories):
    expected = {
        "libraries": 0,
        "tracks": 0,
        "albums": 0,
        "uploads": 0,
        "artists": 0,
        "reports": 0,
        "channels": 0,
        "requests": 0,
        "outbox_activities": 0,
        "received_library_follows": 0,
        "emitted_library_follows": 0,
        "media_total_size": 0,
        "media_downloaded_size": 0,
    }

    actor = factories["federation.Actor"]()

    assert actor.get_stats() == expected


def test_actor_can_manage_false(mocker, factories):
    obj = mocker.Mock()
    actor = factories["federation.Actor"]()

    assert actor.can_manage(obj) is False


def test_actor_can_manage_attributed_to(mocker, factories):
    actor = factories["federation.Actor"]()
    obj = mocker.Mock(attributed_to_id=actor.pk)

    assert actor.can_manage(obj) is True


def test_actor_can_manage_domain_not_service_actor(mocker, factories):
    actor = factories["federation.Actor"]()
    obj = mocker.Mock(fid="https://{}/hello".format(actor.domain_id))

    assert actor.can_manage(obj) is False


def test_actor_can_manage_domain_service_actor(mocker, factories):
    actor = factories["federation.Actor"]()
    actor.domain.service_actor = actor
    actor.domain.save()
    obj = mocker.Mock(fid="https://{}/hello".format(actor.domain_id))

    assert actor.can_manage(obj) is True


def test_can_create_fetch_for_object(factories):
    track = factories["music.Track"](fid="http://test.domain")
    fetch = factories["federation.Fetch"](object=track)
    assert fetch.url == "http://test.domain"
    assert fetch.status == "pending"
    assert fetch.detail == {}
    assert fetch.object == track


@pytest.mark.parametrize(
    "initial_approved, updated_approved, initial_playable_tracks, updated_playable_tracks",
    [
        (
            True,
            False,
            {"owner": [0], "follower": [0], "local_actor": [], None: []},
            {"owner": [0], "follower": [], "local_actor": [], None: []},
        ),
        (
            False,
            True,
            {"owner": [0], "follower": [], "local_actor": [], None: []},
            {"owner": [0], "follower": [0], "local_actor": [], None: []},
        ),
    ],
)
def test_update_library_follow_approved_create_entries(
    initial_approved,
    updated_approved,
    initial_playable_tracks,
    updated_playable_tracks,
    factories,
):
    actors = {
        "owner": factories["federation.Actor"](local=True),
        "follower": factories["federation.Actor"](local=True),
        "local_actor": factories["federation.Actor"](local=True),
        None: None,
    }
    library = factories["music.Library"](actor=actors["owner"], privacy_level="me")

    tracks = [
        factories["music.Upload"](playable=True, library=library).track,
        factories["music.Upload"](library=library, import_status="pending").track,
    ]

    follow = factories["federation.LibraryFollow"](
        target=library, actor=actors["follower"], approved=initial_approved
    )

    for actor_name, expected in initial_playable_tracks.items():
        actor = actors[actor_name]
        expected_tracks = [tracks[i] for i in expected]
        assert list(music_models.Track.objects.playable_by(actor)) == expected_tracks

    follow.approved = updated_approved
    follow.save()

    for actor_name, expected in updated_playable_tracks.items():
        actor = actors[actor_name]
        expected_tracks = [tracks[i] for i in expected]
        assert list(music_models.Track.objects.playable_by(actor)) == expected_tracks


def test_update_library_follow_delete_delete_denormalization_entries(factories,):
    updated_playable_tracks = {"owner": [0], "follower": []}
    actors = {
        "owner": factories["federation.Actor"](local=True),
        "follower": factories["federation.Actor"](local=True),
    }
    library = factories["music.Library"](actor=actors["owner"], privacy_level="me")

    tracks = [
        factories["music.Upload"](playable=True, library=library).track,
        factories["music.Upload"](library=library, import_status="pending").track,
    ]

    follow = factories["federation.LibraryFollow"](
        target=library, actor=actors["follower"], approved=True
    )

    follow.delete()

    for actor_name, expected in updated_playable_tracks.items():
        actor = actors[actor_name]
        expected_tracks = [tracks[i] for i in expected]
        assert list(music_models.Track.objects.playable_by(actor)) == expected_tracks
