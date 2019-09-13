import datetime
import pytest

from django.urls import reverse

from funkwhale_api.users import models
from funkwhale_api.federation import utils as federation_utils


def test__str__(factories):
    user = factories["users.User"](username="hello")
    assert user.__str__() == "hello"


def test_changing_password_updates_subsonic_api_token_no_token(factories):
    user = factories["users.User"](subsonic_api_token=None)
    user.set_password("new")
    assert user.subsonic_api_token is None


def test_changing_password_updates_subsonic_api_token(factories):
    user = factories["users.User"](subsonic_api_token="test")
    user.set_password("new")

    assert user.subsonic_api_token is not None
    assert user.subsonic_api_token != "test"


def test_get_permissions_superuser(factories):
    user = factories["users.User"](is_superuser=True)

    perms = user.get_permissions()
    for p in models.PERMISSIONS:
        assert perms[p] is True


def test_get_permissions_regular(factories):
    user = factories["users.User"](permission_library=True)

    perms = user.get_permissions()
    for p in models.PERMISSIONS:
        if p == "library":
            assert perms[p] is True
        else:
            assert perms[p] is False


def test_get_permissions_default(factories, preferences):
    preferences["users__default_permissions"] = ["library", "moderation"]
    user = factories["users.User"]()

    perms = user.get_permissions()
    assert perms["moderation"] is True
    assert perms["library"] is True
    assert perms["settings"] is False


@pytest.mark.parametrize(
    "args,perms,expected",
    [
        ({"is_superuser": True}, ["moderation", "library"], True),
        ({"is_superuser": False}, ["moderation"], False),
        ({"permission_library": True}, ["library"], True),
        ({"permission_library": True}, ["library", "moderation"], False),
    ],
)
def test_has_permissions_and(args, perms, expected, factories):
    user = factories["users.User"](**args)
    assert user.has_permissions(*perms, operator="and") is expected


@pytest.mark.parametrize(
    "args,perms,expected",
    [
        ({"is_superuser": True}, ["moderation", "library"], True),
        ({"is_superuser": False}, ["moderation"], False),
        ({"permission_library": True}, ["library", "moderation"], True),
        ({"permission_library": True}, ["moderation"], False),
    ],
)
def test_has_permissions_or(args, perms, expected, factories):
    user = factories["users.User"](**args)
    assert user.has_permissions(*perms, operator="or") is expected


def test_record_activity(factories, now):
    user = factories["users.User"]()
    assert user.last_activity is None

    user.record_activity()

    assert user.last_activity == now


def test_record_activity_does_nothing_if_already(factories, now, mocker):
    user = factories["users.User"](last_activity=now)
    save = mocker.patch("funkwhale_api.users.models.User.save")
    user.record_activity()

    save.assert_not_called()


def test_invitation_generates_random_code_on_save(factories):
    invitation = factories["users.Invitation"]()
    assert len(invitation.code) >= 6


def test_invitation_expires_after_delay(factories, settings):
    delay = settings.USERS_INVITATION_EXPIRATION_DAYS
    invitation = factories["users.Invitation"]()
    assert invitation.expiration_date == (
        invitation.creation_date + datetime.timedelta(days=delay)
    )


def test_can_filter_open_invitations(factories):
    okay = factories["users.Invitation"]()
    factories["users.Invitation"](expired=True)
    factories["users.User"](invited=True)

    assert models.Invitation.objects.count() == 3
    assert list(models.Invitation.objects.open()) == [okay]


def test_can_filter_closed_invitations(factories):
    factories["users.Invitation"]()
    expired = factories["users.Invitation"](expired=True)
    used = factories["users.User"](invited=True).invitation

    assert models.Invitation.objects.count() == 3
    assert list(models.Invitation.objects.order_by("id").open(False)) == [expired, used]


def test_creating_actor_from_user(factories, settings):
    user = factories["users.User"](username="Hello M. world")
    actor = models.create_actor(user)

    assert actor.preferred_username == "Hello_M_world"  # slugified
    assert actor.domain.pk == settings.FEDERATION_HOSTNAME
    assert actor.type == "Person"
    assert actor.name == user.username
    assert actor.manually_approves_followers is False
    assert actor.fid == federation_utils.full_url(
        reverse(
            "federation:actors-detail",
            kwargs={"preferred_username": actor.preferred_username},
        )
    )
    assert actor.shared_inbox_url == federation_utils.full_url(
        reverse("federation:shared-inbox")
    )
    assert actor.inbox_url == federation_utils.full_url(
        reverse(
            "federation:actors-inbox",
            kwargs={"preferred_username": actor.preferred_username},
        )
    )
    assert actor.outbox_url == federation_utils.full_url(
        reverse(
            "federation:actors-outbox",
            kwargs={"preferred_username": actor.preferred_username},
        )
    )
    assert actor.followers_url == federation_utils.full_url(
        reverse(
            "federation:actors-followers",
            kwargs={"preferred_username": actor.preferred_username},
        )
    )
    assert actor.following_url == federation_utils.full_url(
        reverse(
            "federation:actors-following",
            kwargs={"preferred_username": actor.preferred_username},
        )
    )


def test_get_channels_groups(factories):
    user = factories["users.User"](permission_library=True)

    assert user.get_channels_groups() == [
        "user.{}.imports".format(user.pk),
        "user.{}.inbox".format(user.pk),
        "admin.library",
    ]


def test_user_quota_default_to_preference(factories, preferences):
    preferences["users__upload_quota"] = 42

    user = factories["users.User"]()
    assert user.get_upload_quota() == 42


def test_user_quota_set_on_user(factories, preferences):
    preferences["users__upload_quota"] = 42

    user = factories["users.User"](upload_quota=66)
    assert user.get_upload_quota() == 66


def test_user_get_quota_status(factories, preferences, mocker):
    user = factories["users.User"](upload_quota=66, with_actor=True)
    mocker.patch(
        "funkwhale_api.federation.models.Actor.get_current_usage",
        return_value={
            "total": 10 * 1000 * 1000,
            "pending": 1 * 1000 * 1000,
            "skipped": 2 * 1000 * 1000,
            "errored": 3 * 1000 * 1000,
            "finished": 4 * 1000 * 1000,
        },
    )
    assert user.get_quota_status() == {
        "max": 66,
        "remaining": 56,
        "current": 10,
        "pending": 1,
        "skipped": 2,
        "errored": 3,
        "finished": 4,
    }


def test_deleting_users_deletes_associated_actor(factories):
    actor = factories["federation.Actor"]()
    user = factories["users.User"](actor=actor)

    user.delete()

    with pytest.raises(actor.DoesNotExist):
        actor.refresh_from_db()
