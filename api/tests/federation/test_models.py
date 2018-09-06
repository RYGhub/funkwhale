import pytest
from django import db


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
    factories["music.TrackFile"](
        library=library,
        import_status="pending",
        audio_file__from_path=None,
        audio_file__data=b"a",
    )
    factories["music.TrackFile"](
        library=library,
        import_status="skipped",
        audio_file__from_path=None,
        audio_file__data=b"aa",
    )
    factories["music.TrackFile"](
        library=library,
        import_status="errored",
        audio_file__from_path=None,
        audio_file__data=b"aaa",
    )
    factories["music.TrackFile"](
        library=library,
        import_status="finished",
        audio_file__from_path=None,
        audio_file__data=b"aaaa",
    )
    expected = {"total": 10, "pending": 1, "skipped": 2, "errored": 3, "finished": 4}

    assert library.actor.get_current_usage() == expected
