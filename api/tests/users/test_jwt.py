import pytest
from jwt.exceptions import DecodeError
from rest_framework_jwt.settings import api_settings


def test_can_invalidate_token_when_changing_user_secret_key(factories):
    user = factories["users.User"]()
    u1 = user.secret_key
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    payload = jwt_payload_handler(user)
    payload = jwt_encode_handler(payload)

    # this should work
    api_settings.JWT_DECODE_HANDLER(payload)

    # now we update the secret key
    user.update_secret_key()
    user.save()
    assert user.secret_key != u1

    # token should be invalid
    with pytest.raises(DecodeError):
        api_settings.JWT_DECODE_HANDLER(payload)
