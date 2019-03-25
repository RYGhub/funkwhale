from oauth2_provider import models
from funkwhale_api.users.oauth import tasks


def test_clear_expired_tokens(mocker, db):
    clear_expired = mocker.spy(models, "clear_expired")

    tasks.clear_expired_tokens()

    clear_expired.assert_called_once()
