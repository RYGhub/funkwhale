import cryptography.exceptions
import io
import pytest
import requests_http_signature

from funkwhale_api.federation import signing


def test_can_sign_and_verify_request(factories):
    private, public = factories['federation.KeyPair']()
    auth = factories['federation.SignatureAuth'](key=private)
    request = factories['federation.SignedRequest'](
        auth=auth
    )
    prepared_request = request.prepare()
    assert 'date' in prepared_request.headers
    assert 'authorization' in prepared_request.headers
    assert prepared_request.headers['authorization'].startswith('Signature')
    assert requests_http_signature.HTTPSignatureAuth.verify(
        prepared_request,
        key_resolver=lambda **kwargs: public
    ) is None


def test_verify_fails_with_wrong_key(factories):
    wrong_private, wrong_public = factories['federation.KeyPair']()
    request = factories['federation.SignedRequest']()
    prepared_request = request.prepare()

    with pytest.raises(cryptography.exceptions.InvalidSignature):
        requests_http_signature.HTTPSignatureAuth.verify(
            prepared_request,
            key_resolver=lambda **kwargs: wrong_public
        )
