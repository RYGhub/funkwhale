import requests
import requests_http_signature

from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend


def get_key_pair(size=2048):
    key = rsa.generate_private_key(
        backend=crypto_default_backend(),
        public_exponent=65537,
        key_size=size
    )
    private_key = key.private_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PrivateFormat.PKCS8,
        crypto_serialization.NoEncryption())
    public_key = key.public_key().public_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PublicFormat.PKCS1
    )

    return private_key, public_key


def verify(request, public_key):
    return requests_http_signature.HTTPSignatureAuth.verify(
        request,
        key_resolver=lambda **kwargs: public_key
    )


def verify_django(django_request, public_key):
    """
    Given a django WSGI request, create an underlying requests.PreparedRequest
    instance we can verify
    """
    headers = django_request.META.get('headers', {}).copy()
    for h, v in list(headers.items()):
        # we include lower-cased version of the headers for compatibility
        # with requests_http_signature
        headers[h.lower()] = v
    try:
        signature = headers['authorization']
    except KeyError:
        raise exceptions.MissingSignature

    request = requests.Request(
        method=django_request.method,
        url='http://noop',
        data=django_request.body,
        headers=headers)

    prepared_request = request.prepare()
    return verify(request, public_key)
