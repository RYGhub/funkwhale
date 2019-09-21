from funkwhale_api.users import tasks


def test_delete_account_mutation(mocker, factories, now):
    user = factories["users.User"](subsonic_api_token="test", password="test")
    actor = user.create_actor()
    on_commit = mocker.patch("funkwhale_api.common.utils.on_commit")

    secret_key = user.secret_key
    set_unusable_password = mocker.spy(user, "set_unusable_password")
    factories["users.Grant"](user=user)
    factories["users.AccessToken"](user=user)
    factories["users.RefreshToken"](user=user)
    mutation = factories["common.Mutation"](
        type="delete_account", target=actor, payload={}
    )

    mutation.apply()
    user.refresh_from_db()

    set_unusable_password.assert_called_once_with()
    assert user.has_usable_password() is False
    assert user.subsonic_api_token is None
    assert user.secret_key is not None and user.secret_key != secret_key
    assert user.users_grant.count() == 0
    assert user.users_refreshtoken.count() == 0
    assert user.users_accesstoken.count() == 0
    on_commit.assert_called_once_with(tasks.delete_account.delay, user_id=user.pk)

    assert mutation.previous_state == {
        "actor": {"preferred_username": actor.preferred_username},
        "user": {"username": user.username, "id": user.pk},
    }
