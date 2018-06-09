import pytest

from rest_framework_jwt.settings import api_settings

from funkwhale_api.common.auth import TokenAuthMiddleware

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


@pytest.mark.parametrize("query_string", [b"token=wrong", b""])
def test_header_anonymous(query_string, factories):
    def callback(scope):
        assert scope["user"].is_anonymous

    scope = {"query_string": query_string}
    consumer = TokenAuthMiddleware(callback)
    consumer(scope)


def test_header_correct_token(factories):
    user = factories["users.User"]()
    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)

    def callback(scope):
        assert scope["user"] == user

    scope = {"query_string": "token={}".format(token).encode("utf-8")}
    consumer = TokenAuthMiddleware(callback)
    consumer(scope)
