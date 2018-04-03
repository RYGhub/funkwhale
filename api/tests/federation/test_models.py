import pytest

from django import db

from funkwhale_api.federation import models


def test_cannot_duplicate_actor(factories):
    actor = factories['federation.Actor']()

    with pytest.raises(db.IntegrityError):
        factories['federation.Actor'](
            domain=actor.domain,
            preferred_username=actor.preferred_username,
        )


def test_cannot_duplicate_follow(factories):
    follow = factories['federation.Follow']()

    with pytest.raises(db.IntegrityError):
        factories['federation.Follow'](
            target=follow.target,
            actor=follow.actor,
        )

def test_follow_federation_url(factories):
    follow = factories['federation.Follow'](local=True)
    expected = '{}#follows/{}'.format(
        follow.actor.url, follow.uuid)

    assert follow.get_federation_url() == expected
