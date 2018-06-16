import pytest

from funkwhale_api.federation import keys


@pytest.mark.parametrize(
    "raw, expected",
    [
        ('algorithm="test",keyId="https://test.com"', "https://test.com"),
        ('keyId="https://test.com",algorithm="test"', "https://test.com"),
    ],
)
def test_get_key_from_header(raw, expected):
    r = keys.get_key_id_from_signature_header(raw)
    assert r == expected


@pytest.mark.parametrize(
    "raw",
    [
        'algorithm="test",keyid="badCase"',
        'algorithm="test",wrong="wrong"',
        'keyId = "wrong"',
        "keyId='wrong'",
        'keyId="notanurl"',
        'keyId="wrong://test.com"',
    ],
)
def test_get_key_from_header_invalid(raw):
    with pytest.raises(ValueError):
        keys.get_key_id_from_signature_header(raw)
