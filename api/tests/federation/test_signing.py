import cryptography.exceptions
import io
import pytest
import requests_http_signature

from funkwhale_api.federation import signing
from funkwhale_api.federation import keys


def test_can_sign_and_verify_request(nodb_factories):
    private, public = nodb_factories['federation.KeyPair']()
    auth = nodb_factories['federation.SignatureAuth'](key=private)
    request = nodb_factories['federation.SignedRequest'](
        auth=auth
    )
    prepared_request = request.prepare()
    assert 'date' in prepared_request.headers
    assert 'signature' in prepared_request.headers
    assert signing.verify(
        prepared_request, public) is None


def test_can_sign_and_verify_request_digest(nodb_factories):
    private, public = nodb_factories['federation.KeyPair']()
    auth = nodb_factories['federation.SignatureAuth'](key=private)
    request = nodb_factories['federation.SignedRequest'](
        auth=auth,
        method='post',
        data=b'hello=world'
    )
    prepared_request = request.prepare()
    assert 'date' in prepared_request.headers
    assert 'digest' in prepared_request.headers
    assert 'signature' in prepared_request.headers
    assert signing.verify(prepared_request, public) is None


def test_verify_fails_with_wrong_key(nodb_factories):
    wrong_private, wrong_public = nodb_factories['federation.KeyPair']()
    request = nodb_factories['federation.SignedRequest']()
    prepared_request = request.prepare()

    with pytest.raises(cryptography.exceptions.InvalidSignature):
        signing.verify(prepared_request, wrong_public)


def test_can_verify_django_request(factories, api_request):
    private_key, public_key = keys.get_key_pair()
    signed_request = factories['federation.SignedRequest'](
        auth__key=private_key
    )
    prepared = signed_request.prepare()
    django_request = api_request.get(
        '/',
        headers={
            'Date': prepared.headers['date'],
            'Signature': prepared.headers['signature'],
        }
    )
    assert signing.verify_django(django_request, public_key) is None


def test_can_verify_django_request_digest(factories, api_request):
    private_key, public_key = keys.get_key_pair()
    signed_request = factories['federation.SignedRequest'](
        auth__key=private_key,
        method='post',
        data=b'hello=world'
    )
    prepared = signed_request.prepare()
    django_request = api_request.post(
        '/',
        headers={
            'Date': prepared.headers['date'],
            'Digest': prepared.headers['digest'],
            'Signature': prepared.headers['signature'],
        }
    )

    assert signing.verify_django(django_request, public_key) is None


def test_can_verify_django_request_digest_failure(factories, api_request):
    private_key, public_key = keys.get_key_pair()
    signed_request = factories['federation.SignedRequest'](
        auth__key=private_key,
        method='post',
        data=b'hello=world'
    )
    prepared = signed_request.prepare()
    django_request = api_request.post(
        '/',
        headers={
            'Date': prepared.headers['date'],
            'Digest': prepared.headers['digest'] + 'noop',
            'Signature': prepared.headers['signature'],
        }
    )

    with pytest.raises(cryptography.exceptions.InvalidSignature):
        signing.verify_django(django_request, public_key)


def test_can_verify_django_request_failure(factories, api_request):
    private_key, public_key = keys.get_key_pair()
    signed_request = factories['federation.SignedRequest'](
        auth__key=private_key
    )
    prepared = signed_request.prepare()
    django_request = api_request.get(
        '/',
        headers={
            'Date': 'Wrong',
            'Signature': prepared.headers['signature'],
        }
    )
    with pytest.raises(cryptography.exceptions.InvalidSignature):
        signing.verify_django(django_request, public_key)
