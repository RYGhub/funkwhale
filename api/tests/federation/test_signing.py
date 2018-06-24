import cryptography.exceptions
import datetime
from django.utils.http import http_date
from django import forms
import pytest

from funkwhale_api.federation import keys, signing


def test_can_sign_and_verify_request(nodb_factories):
    private, public = nodb_factories["federation.KeyPair"]()
    auth = nodb_factories["federation.SignatureAuth"](key=private)
    request = nodb_factories["federation.SignedRequest"](auth=auth)
    prepared_request = request.prepare()
    assert "date" in prepared_request.headers
    assert "signature" in prepared_request.headers
    assert signing.verify(prepared_request, public) is None


def test_can_sign_and_verify_request_digest(nodb_factories):
    private, public = nodb_factories["federation.KeyPair"]()
    auth = nodb_factories["federation.SignatureAuth"](key=private)
    request = nodb_factories["federation.SignedRequest"](
        auth=auth, method="post", data=b"hello=world"
    )
    prepared_request = request.prepare()
    assert "date" in prepared_request.headers
    assert "digest" in prepared_request.headers
    assert "signature" in prepared_request.headers
    assert signing.verify(prepared_request, public) is None


def test_verify_fails_with_wrong_key(nodb_factories):
    wrong_private, wrong_public = nodb_factories["federation.KeyPair"]()
    request = nodb_factories["federation.SignedRequest"]()
    prepared_request = request.prepare()

    with pytest.raises(cryptography.exceptions.InvalidSignature):
        signing.verify(prepared_request, wrong_public)


def test_verify_fails_with_wrong_date(nodb_factories, now):
    too_old = now - datetime.timedelta(seconds=31)
    too_old = http_date(too_old.timestamp())
    private, public = nodb_factories["federation.KeyPair"]()
    auth = nodb_factories["federation.SignatureAuth"](key=private)
    request = nodb_factories["federation.SignedRequest"](
        auth=auth, headers={"Date": too_old}
    )
    prepared_request = request.prepare()

    with pytest.raises(forms.ValidationError):
        signing.verify(prepared_request, public)


def test_can_verify_django_request(factories, fake_request):
    private_key, public_key = keys.get_key_pair()
    signed_request = factories["federation.SignedRequest"](
        auth__key=private_key, auth__headers=["date"]
    )
    prepared = signed_request.prepare()
    django_request = fake_request.get(
        "/",
        **{
            "HTTP_DATE": prepared.headers["date"],
            "HTTP_SIGNATURE": prepared.headers["signature"],
        }
    )
    assert signing.verify_django(django_request, public_key) is None


def test_can_verify_django_request_digest(factories, fake_request):
    private_key, public_key = keys.get_key_pair()
    signed_request = factories["federation.SignedRequest"](
        auth__key=private_key,
        method="post",
        data=b"hello=world",
        auth__headers=["date", "digest"],
    )
    prepared = signed_request.prepare()
    django_request = fake_request.post(
        "/",
        **{
            "HTTP_DATE": prepared.headers["date"],
            "HTTP_DIGEST": prepared.headers["digest"],
            "HTTP_SIGNATURE": prepared.headers["signature"],
        }
    )

    assert signing.verify_django(django_request, public_key) is None


def test_can_verify_django_request_digest_failure(factories, fake_request):
    private_key, public_key = keys.get_key_pair()
    signed_request = factories["federation.SignedRequest"](
        auth__key=private_key,
        method="post",
        data=b"hello=world",
        auth__headers=["date", "digest"],
    )
    prepared = signed_request.prepare()
    django_request = fake_request.post(
        "/",
        **{
            "HTTP_DATE": prepared.headers["date"],
            "HTTP_DIGEST": prepared.headers["digest"] + "noop",
            "HTTP_SIGNATURE": prepared.headers["signature"],
        }
    )

    with pytest.raises(cryptography.exceptions.InvalidSignature):
        signing.verify_django(django_request, public_key)


def test_can_verify_django_request_failure(factories, fake_request, now):
    private_key, public_key = keys.get_key_pair()
    signed_request = factories["federation.SignedRequest"](
        auth__key=private_key, auth__headers=["date"]
    )
    prepared = signed_request.prepare()
    django_request = fake_request.get(
        "/",
        **{
            "HTTP_DATE": http_date((now + datetime.timedelta(seconds=31)).timestamp()),
            "HTTP_SIGNATURE": prepared.headers["signature"],
        }
    )
    with pytest.raises(forms.ValidationError):
        signing.verify_django(django_request, public_key)
