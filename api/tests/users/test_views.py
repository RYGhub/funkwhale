import pytest
from django.urls import reverse

from funkwhale_api.users.models import User


def test_can_create_user_via_api(preferences, api_client, db):
    url = reverse("rest_register")
    data = {
        "username": "test1",
        "email": "test1@test.com",
        "password1": "testtest",
        "password2": "testtest",
    }
    preferences["users__registration_enabled"] = True
    response = api_client.post(url, data)
    assert response.status_code == 201

    u = User.objects.get(email="test1@test.com")
    assert u.username == "test1"


def test_can_restrict_usernames(settings, preferences, db, api_client):
    url = reverse("rest_register")
    preferences["users__registration_enabled"] = True
    settings.USERNAME_BLACKLIST = ["funkwhale"]
    data = {
        "username": "funkwhale",
        "email": "contact@funkwhale.io",
        "password1": "testtest",
        "password2": "testtest",
    }

    response = api_client.post(url, data)

    assert response.status_code == 400
    assert "username" in response.data


def test_can_disable_registration_view(preferences, api_client, db):
    url = reverse("rest_register")
    data = {
        "username": "test1",
        "email": "test1@test.com",
        "password1": "testtest",
        "password2": "testtest",
    }
    preferences["users__registration_enabled"] = False
    response = api_client.post(url, data)
    assert response.status_code == 403


def test_can_signup_with_invitation(preferences, factories, api_client):
    url = reverse("rest_register")
    invitation = factories["users.Invitation"](code="Hello")
    data = {
        "username": "test1",
        "email": "test1@test.com",
        "password1": "testtest",
        "password2": "testtest",
        "invitation": "hello",
    }
    preferences["users__registration_enabled"] = False
    response = api_client.post(url, data)
    assert response.status_code == 201
    u = User.objects.get(email="test1@test.com")
    assert u.username == "test1"
    assert u.invitation == invitation


def test_can_signup_with_invitation_invalid(preferences, factories, api_client):
    url = reverse("rest_register")
    factories["users.Invitation"](code="hello")
    data = {
        "username": "test1",
        "email": "test1@test.com",
        "password1": "testtest",
        "password2": "testtest",
        "invitation": "nope",
    }
    response = api_client.post(url, data)
    assert response.status_code == 400
    assert "invitation" in response.data


def test_can_fetch_data_from_api(api_client, factories):
    url = reverse("api:v1:users:users-me")
    response = api_client.get(url)
    # login required
    assert response.status_code == 401

    user = factories["users.User"](permission_library=True)
    api_client.login(username=user.username, password="test")
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data["username"] == user.username
    assert response.data["is_staff"] == user.is_staff
    assert response.data["is_superuser"] == user.is_superuser
    assert response.data["email"] == user.email
    assert response.data["name"] == user.name
    assert response.data["permissions"] == user.get_permissions()


def test_can_get_token_via_api(api_client, factories):
    user = factories["users.User"]()
    url = reverse("api:v1:token")
    payload = {"username": user.username, "password": "test"}

    response = api_client.post(url, payload)
    assert response.status_code == 200
    assert "token" in response.data


def test_can_get_token_via_api_inactive(api_client, factories):
    user = factories["users.User"](is_active=False)
    url = reverse("api:v1:token")
    payload = {"username": user.username, "password": "test"}

    response = api_client.post(url, payload)
    assert response.status_code == 400


def test_can_refresh_token_via_api(api_client, factories, mocker):
    # first, we get a token
    user = factories["users.User"]()
    url = reverse("api:v1:token")
    payload = {"username": user.username, "password": "test"}

    response = api_client.post(url, payload)
    assert response.status_code == 200

    token = response.data["token"]
    url = reverse("api:v1:token_refresh")
    response = api_client.post(url, {"token": token})

    assert response.status_code == 200
    assert "token" in response.data


def test_changing_password_updates_secret_key(logged_in_api_client):
    user = logged_in_api_client.user
    password = user.password
    secret_key = user.secret_key
    payload = {"old_password": "test", "new_password1": "new", "new_password2": "new"}
    url = reverse("change_password")

    logged_in_api_client.post(url, payload)

    user.refresh_from_db()

    assert user.secret_key != secret_key
    assert user.password != password


def test_can_request_password_reset(factories, api_client, mailoutbox):
    user = factories["users.User"]()
    payload = {"email": user.email}
    emails = len(mailoutbox)
    url = reverse("rest_password_reset")

    response = api_client.post(url, payload)
    assert response.status_code == 200
    assert len(mailoutbox) > emails


def test_user_can_patch_his_own_settings(logged_in_api_client):
    user = logged_in_api_client.user
    payload = {"privacy_level": "me"}
    url = reverse("api:v1:users:users-detail", kwargs={"username": user.username})

    response = logged_in_api_client.patch(url, payload)

    assert response.status_code == 200
    user.refresh_from_db()

    assert user.privacy_level == "me"


def test_user_can_request_new_subsonic_token(logged_in_api_client):
    user = logged_in_api_client.user
    user.subsonic_api_token = "test"
    user.save()

    url = reverse(
        "api:v1:users:users-subsonic-token", kwargs={"username": user.username}
    )

    response = logged_in_api_client.post(url)

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.subsonic_api_token != "test"
    assert user.subsonic_api_token is not None
    assert response.data == {"subsonic_api_token": user.subsonic_api_token}


def test_user_can_get_subsonic_token(logged_in_api_client):
    user = logged_in_api_client.user
    user.subsonic_api_token = "test"
    user.save()

    url = reverse(
        "api:v1:users:users-subsonic-token", kwargs={"username": user.username}
    )

    response = logged_in_api_client.get(url)

    assert response.status_code == 200
    assert response.data == {"subsonic_api_token": "test"}


def test_user_can_delete_subsonic_token(logged_in_api_client):
    user = logged_in_api_client.user
    user.subsonic_api_token = "test"
    user.save()

    url = reverse(
        "api:v1:users:users-subsonic-token", kwargs={"username": user.username}
    )

    response = logged_in_api_client.delete(url)

    assert response.status_code == 204
    user.refresh_from_db()
    assert user.subsonic_api_token is None


@pytest.mark.parametrize("method", ["put", "patch"])
def test_user_cannot_patch_another_user(method, logged_in_api_client, factories):
    user = factories["users.User"]()
    payload = {"privacy_level": "me"}
    url = reverse("api:v1:users:users-detail", kwargs={"username": user.username})

    handler = getattr(logged_in_api_client, method)
    response = handler(url, payload)

    assert response.status_code == 403


def test_user_can_patch_their_own_avatar(logged_in_api_client, avatar):
    user = logged_in_api_client.user
    url = reverse("api:v1:users:users-detail", kwargs={"username": user.username})
    content = avatar.read()
    avatar.seek(0)
    payload = {"avatar": avatar}
    response = logged_in_api_client.patch(url, payload)

    assert response.status_code == 200
    user.refresh_from_db()

    assert user.avatar.read() == content
