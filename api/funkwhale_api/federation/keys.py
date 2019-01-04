import re
import urllib.parse

from django.conf import settings

from cryptography.hazmat.backends import default_backend as crypto_default_backend
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa

KEY_ID_REGEX = re.compile(r"keyId=\"(?P<id>.*)\"")


def get_key_pair(size=None):
    size = size or settings.RSA_KEY_SIZE
    key = rsa.generate_private_key(
        backend=crypto_default_backend(), public_exponent=65537, key_size=size
    )
    private_key = key.private_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PrivateFormat.PKCS8,
        crypto_serialization.NoEncryption(),
    )
    public_key = key.public_key().public_bytes(
        crypto_serialization.Encoding.PEM, crypto_serialization.PublicFormat.PKCS1
    )

    return private_key, public_key


def get_key_id_from_signature_header(header_string):
    parts = header_string.split(",")
    try:
        raw_key_id = [p for p in parts if p.startswith('keyId="')][0]
    except IndexError:
        raise ValueError("Missing key id")

    match = KEY_ID_REGEX.match(raw_key_id)
    if not match:
        raise ValueError("Invalid key id")

    key_id = match.groups()[0]
    url = urllib.parse.urlparse(key_id)
    if not url.scheme or not url.netloc:
        raise ValueError("Invalid url")
    if url.scheme not in ["http", "https"]:
        raise ValueError("Invalid shceme")
    return key_id
