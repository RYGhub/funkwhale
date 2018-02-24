import json

from django.test import RequestFactory
from django.urls import reverse

from funkwhale_api.users.models import User


def test_can_create_user_via_api(preferences, client, db):
    url = reverse('rest_register')
    data = {
        'username': 'test1',
        'email': 'test1@test.com',
        'password1': 'testtest',
        'password2': 'testtest',
    }
    preferences['users__registration_enabled'] = True
    response = client.post(url, data)
    assert response.status_code == 201

    u = User.objects.get(email='test1@test.com')
    assert u.username == 'test1'


def test_can_disable_registration_view(preferences, client, db):
    url = reverse('rest_register')
    data = {
        'username': 'test1',
        'email': 'test1@test.com',
        'password1': 'testtest',
        'password2': 'testtest',
    }
    preferences['users__registration_enabled'] = False
    response = client.post(url, data)
    assert response.status_code == 403


def test_can_fetch_data_from_api(client, factories):
    url = reverse('api:v1:users:users-me')
    response = client.get(url)
    # login required
    assert response.status_code == 401

    user = factories['users.User'](
        is_staff=True,
        perms=[
            'music.add_importbatch',
            'dynamic_preferences.change_globalpreferencemodel',
        ]
    )
    assert user.has_perm('music.add_importbatch')
    client.login(username=user.username, password='test')
    response = client.get(url)
    assert response.status_code == 200

    payload = json.loads(response.content.decode('utf-8'))

    assert payload['username'] == user.username
    assert payload['is_staff'] == user.is_staff
    assert payload['is_superuser'] == user.is_superuser
    assert payload['email'] == user.email
    assert payload['name'] == user.name
    assert payload['permissions']['import.launch']['status']
    assert payload['permissions']['settings.change']['status']


def test_can_get_token_via_api(client, factories):
    user = factories['users.User']()
    url = reverse('api:v1:token')
    payload = {
        'username': user.username,
        'password': 'test'
    }

    response = client.post(url, payload)
    assert response.status_code == 200
    assert '"token":' in response.content.decode('utf-8')


def test_can_refresh_token_via_api(client, factories):
    # first, we get a token
    user = factories['users.User']()
    url = reverse('api:v1:token')
    payload = {
        'username': user.username,
        'password': 'test'
    }

    response = client.post(url, payload)
    assert response.status_code == 200

    token = json.loads(response.content.decode('utf-8'))['token']
    url = reverse('api:v1:token_refresh')
    response = client.post(url,{'token': token})

    assert response.status_code == 200
    assert '"token":' in response.content.decode('utf-8')
    # a different token should be returned
    assert token in response.content.decode('utf-8')


def test_changing_password_updates_secret_key(logged_in_client):
    user = logged_in_client.user
    password = user.password
    secret_key = user.secret_key
    payload = {
        'old_password': 'test',
        'new_password1': 'new',
        'new_password2': 'new',
    }
    url = reverse('change_password')

    response = logged_in_client.post(url, payload)

    user.refresh_from_db()

    assert user.secret_key != secret_key
    assert user.password != password
