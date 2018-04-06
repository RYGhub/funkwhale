import pytest
import uuid

from django import db

from funkwhale_api.federation import models
from funkwhale_api.federation import serializers


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


def test_follow_request_approve(mocker, factories):
    uid = uuid.uuid4()
    mocker.patch('uuid.uuid4', return_value=uid)
    accept_follow = mocker.patch(
        'funkwhale_api.federation.activity.accept_follow')
    fr = factories['federation.FollowRequest'](target__local=True)
    fr.approve()

    follow = {
        '@context': serializers.AP_CONTEXT,
        'actor': fr.actor.url,
        'id': fr.actor.url + '#follows/{}'.format(uid),
        'object': fr.target.url,
        'type': 'Follow'
    }

    assert fr.approved is True
    assert list(fr.target.followers.all()) == [fr.actor]
    accept_follow.assert_called_once_with(
        fr.target, follow, fr.actor
    )


def test_follow_request_approve_non_local(mocker, factories):
    uid = uuid.uuid4()
    mocker.patch('uuid.uuid4', return_value=uid)
    accept_follow = mocker.patch(
        'funkwhale_api.federation.activity.accept_follow')
    fr = factories['federation.FollowRequest']()
    fr.approve()

    assert fr.approved is True
    assert list(fr.target.followers.all()) == [fr.actor]
    accept_follow.assert_not_called()


def test_follow_request_refused(mocker, factories):
    fr = factories['federation.FollowRequest']()
    fr.refuse()

    assert fr.approved is False
    assert fr.target.followers.count() == 0


def test_library_model_unique_per_actor(factories):
    library = factories['federation.Library']()
    with pytest.raises(db.IntegrityError):
        factories['federation.Library'](actor=library.actor)
