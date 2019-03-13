from django.contrib import auth
from django.urls import reverse


def test_restricted_access(api_client, db):
    url = reverse("api:v1:artists-list")
    response = api_client.get(url)

    assert response.status_code == 401


def test_login_correct(api_client, factories, mocker):
    login = mocker.spy(auth, "login")
    password = "hellotest"
    user = factories["users.User"]()
    user.set_password(password)
    user.save()

    url = reverse("api:v1:auth:login")
    data = {"username": user.username, "password": password}
    expected = {}
    response = api_client.post(url, data)

    assert response.status_code == 200
    assert response.data == expected
    login.assert_called_once_with(request=mocker.ANY, user=user)


def test_login_incorrect(api_client, factories, mocker):
    login = mocker.spy(auth, "login")
    user = factories["users.User"]()

    url = reverse("api:v1:auth:login")
    data = {"username": user.username, "password": "invalid"}
    response = api_client.post(url, data)

    assert response.status_code == 400

    login.assert_not_called()


def test_login_inactive(api_client, factories, mocker):
    login = mocker.spy(auth, "login")
    password = "hellotest"
    user = factories["users.User"](is_active=False)
    user.set_password(password)
    user.save()

    url = reverse("api:v1:auth:login")
    data = {"username": user.username, "password": password}
    response = api_client.post(url, data)

    assert response.status_code == 400
    assert "Invalid username or password" in response.data["non_field_errors"]

    login.assert_not_called()


def test_logout(logged_in_api_client, factories, mocker):
    logout = mocker.spy(auth, "logout")

    url = reverse("api:v1:auth:logout")
    response = logged_in_api_client.post(url)

    assert response.status_code == 200
    assert response.data == {}
    logout.assert_called_once_with(request=mocker.ANY)


def test_logout_real(api_client, factories):
    password = "hellotest"
    user = factories["users.User"]()
    user.set_password(password)
    user.save()

    url = reverse("api:v1:auth:login")
    data = {"username": user.username, "password": password}
    response = api_client.post(url, data)

    url = reverse("api:v1:auth:logout")
    response = api_client.post(url)

    url = reverse("api:v1:artists-list")
    response = api_client.get(url)

    assert response.status_code == 401
