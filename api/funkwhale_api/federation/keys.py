from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend

import requests

from . import exceptions


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


def get_public_key(actor_url):
    """
    Given an actor_url, request it and extract publicKey data from
    the response payload.
    """
    response = requests.get(actor_url)
    response.raise_for_status()
    payload = response.json()
    try:
        return {
            'public_key_pem': payload['publicKey']['publicKeyPem'],
            'id': payload['publicKey']['id'],
            'owner': payload['publicKey']['owner'],
        }
    except KeyError:
        raise exceptions.MalformedPayload(str(payload))
