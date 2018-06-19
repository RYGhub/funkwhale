import pytest

from funkwhale_api.users import models


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
    preferences["users__default_permissions"] = ["upload", "federation"]
    user = factories["users.User"]()

    perms = user.get_permissions()
    assert perms["upload"] is True
    assert perms["federation"] is True
    assert perms["library"] is False
    assert perms["settings"] is False


@pytest.mark.parametrize(
    "args,perms,expected",
    [
        ({"is_superuser": True}, ["federation", "library"], True),
        ({"is_superuser": False}, ["federation"], False),
        ({"permission_library": True}, ["library"], True),
        ({"permission_library": True}, ["library", "federation"], False),
    ],
)
def test_has_permissions_and(args, perms, expected, factories):
    user = factories["users.User"](**args)
    assert user.has_permissions(*perms, operator="and") is expected


@pytest.mark.parametrize(
    "args,perms,expected",
    [
        ({"is_superuser": True}, ["federation", "library"], True),
        ({"is_superuser": False}, ["federation"], False),
        ({"permission_library": True}, ["library", "federation"], True),
        ({"permission_library": True}, ["federation"], False),
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
