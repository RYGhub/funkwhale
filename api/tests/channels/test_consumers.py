from funkwhale_api.common import consumers


def test_auth_consumer_requires_valid_user(mocker):
    m = mocker.patch("funkwhale_api.common.consumers.JsonAuthConsumer.close")
    scope = {"user": None}
    consumer = consumers.JsonAuthConsumer(scope=scope)
    consumer.connect()
    m.assert_called_once_with()


def test_auth_consumer_requires_user_in_scope(mocker):
    m = mocker.patch("funkwhale_api.common.consumers.JsonAuthConsumer.close")
    scope = {}
    consumer = consumers.JsonAuthConsumer(scope=scope)
    consumer.connect()
    m.assert_called_once_with()


def test_auth_consumer_accepts_connection(mocker, factories):
    user = factories["users.User"]()
    m = mocker.patch("funkwhale_api.common.consumers.JsonAuthConsumer.accept")
    scope = {"user": user}
    consumer = consumers.JsonAuthConsumer(scope=scope)
    consumer.connect()
    m.assert_called_once_with()
