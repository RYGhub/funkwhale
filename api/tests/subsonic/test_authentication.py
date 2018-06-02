import binascii
import pytest

from rest_framework import exceptions

from funkwhale_api.subsonic import authentication


def test_auth_with_salt(api_request, factories):
    salt = 'salt'
    user = factories['users.User']()
    user.subsonic_api_token = 'password'
    user.save()
    token = authentication.get_token(salt, 'password')
    request = api_request.get('/', {
        't': token,
        's': salt,
        'u': user.username
    })

    authenticator = authentication.SubsonicAuthentication()
    u, _ = authenticator.authenticate(request)

    assert user == u


def test_auth_with_password_hex(api_request, factories):
    salt = 'salt'
    user = factories['users.User']()
    user.subsonic_api_token = 'password'
    user.save()
    token = authentication.get_token(salt, 'password')
    request = api_request.get('/', {
        'u': user.username,
        'p': 'enc:{}'.format(binascii.hexlify(
            user.subsonic_api_token.encode('utf-8')).decode('utf-8'))
    })

    authenticator = authentication.SubsonicAuthentication()
    u, _ = authenticator.authenticate(request)

    assert user == u


def test_auth_with_password_cleartext(api_request, factories):
    salt = 'salt'
    user = factories['users.User']()
    user.subsonic_api_token = 'password'
    user.save()
    token = authentication.get_token(salt, 'password')
    request = api_request.get('/', {
        'u': user.username,
        'p': 'password',
    })

    authenticator = authentication.SubsonicAuthentication()
    u, _ = authenticator.authenticate(request)

    assert user == u


def test_auth_with_inactive_users(api_request, factories):
    salt = 'salt'
    user = factories['users.User'](is_active=False)
    user.subsonic_api_token = 'password'
    user.save()
    token = authentication.get_token(salt, 'password')
    request = api_request.get('/', {
        'u': user.username,
        'p': 'password',
    })

    authenticator = authentication.SubsonicAuthentication()
    with pytest.raises(exceptions.AuthenticationFailed):
        authenticator.authenticate(request)
