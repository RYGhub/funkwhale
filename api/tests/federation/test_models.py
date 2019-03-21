import pytest
from django import db

from funkwhale_api.federation import models


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

    expected = {"total": 14, "pending": 1, "skipped": 2, "errored": 3, "finished": 8}

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
        "outbox_activities": 0,
        "received_library_follows": 0,
        "emitted_library_follows": 0,
        "media_total_size": 0,
        "media_downloaded_size": 0,
    }

    actor = factories["federation.Actor"]()

    assert actor.get_stats() == expected
