import pytest

from funkwhale_api.cli import users


def test_user_create_handler(factories, mocker, now):
    kwargs = {
        "username": "helloworld",
        "password": "securepassword",
        "is_superuser": False,
        "is_staff": True,
        "email": "hello@world.email",
        "upload_quota": 35,
        "permissions": ["moderation"],
    }
    set_password = mocker.spy(users.models.User, "set_password")
    create_actor = mocker.spy(users.models, "create_actor")
    user = users.handler_create_user(**kwargs)

    assert user.username == kwargs["username"]
    assert user.is_superuser == kwargs["is_superuser"]
    assert user.is_staff == kwargs["is_staff"]
    assert user.date_joined >= now
    assert user.upload_quota == kwargs["upload_quota"]
    set_password.assert_called_once_with(user, kwargs["password"])
    create_actor.assert_called_once_with(user)

    expected_permissions = {
        p: p in kwargs["permissions"] for p in users.models.PERMISSIONS
    }

    assert user.all_permissions == expected_permissions


def test_user_delete_handler_soft(factories, mocker, now):
    user1 = factories["federation.Actor"](local=True).user
    actor1 = user1.actor
    user2 = factories["federation.Actor"](local=True).user
    actor2 = user2.actor
    user3 = factories["federation.Actor"](local=True).user
    delete_account = mocker.spy(users.tasks, "delete_account")
    users.handler_delete_user([user1.username, user2.username, "unknown"])

    assert delete_account.call_count == 2
    delete_account.assert_any_call(user_id=user1.pk)
    with pytest.raises(user1.DoesNotExist):
        user1.refresh_from_db()

    delete_account.assert_any_call(user_id=user2.pk)
    with pytest.raises(user2.DoesNotExist):
        user2.refresh_from_db()

    # soft delete, actor shouldn't be deleted
    actor1.refresh_from_db()
    actor2.refresh_from_db()

    # not deleted
    user3.refresh_from_db()


def test_user_delete_handler_hard(factories, mocker, now):
    user1 = factories["federation.Actor"](local=True).user
    actor1 = user1.actor
    user2 = factories["federation.Actor"](local=True).user
    actor2 = user2.actor
    user3 = factories["federation.Actor"](local=True).user
    delete_account = mocker.spy(users.tasks, "delete_account")
    users.handler_delete_user([user1.username, user2.username, "unknown"], soft=False)

    assert delete_account.call_count == 2
    delete_account.assert_any_call(user_id=user1.pk)
    with pytest.raises(user1.DoesNotExist):
        user1.refresh_from_db()

    delete_account.assert_any_call(user_id=user2.pk)
    with pytest.raises(user2.DoesNotExist):
        user2.refresh_from_db()

    # hard delete, actors are deleted as well
    with pytest.raises(actor1.DoesNotExist):
        actor1.refresh_from_db()

    with pytest.raises(actor2.DoesNotExist):
        actor2.refresh_from_db()

    # not deleted
    user3.refresh_from_db()


@pytest.mark.parametrize(
    "params, expected",
    [
        ({"is_active": False}, {"is_active": False}),
        (
            {"is_staff": True, "is_superuser": True},
            {"is_staff": True, "is_superuser": True},
        ),
        ({"upload_quota": 35}, {"upload_quota": 35}),
        (
            {
                "permission_library": True,
                "permission_moderation": True,
                "permission_settings": True,
            },
            {
                "all_permissions": {
                    "library": True,
                    "moderation": True,
                    "settings": True,
                }
            },
        ),
    ],
)
def test_user_update_handler(params, expected, factories):
    user1 = factories["federation.Actor"](local=True).user
    user2 = factories["federation.Actor"](local=True).user
    user3 = factories["federation.Actor"](local=True).user

    def get_field_values(user):
        return {f: getattr(user, f) for f, v in expected.items()}

    unchanged = get_field_values(user3)

    users.handler_update_user([user1.username, user2.username, "unknown"], params)

    user1.refresh_from_db()
    user2.refresh_from_db()
    user3.refresh_from_db()

    assert get_field_values(user1) == expected
    assert get_field_values(user2) == expected
    assert get_field_values(user3) == unchanged


def test_user_update_handler_password(factories, mocker):
    user = factories["federation.Actor"](local=True).user
    current_password = user.password

    set_password = mocker.spy(users.models.User, "set_password")

    users.handler_update_user([user.username], {"password": "hello"})

    user.refresh_from_db()

    set_password.assert_called_once_with(user, "hello")
    assert user.password != current_password
