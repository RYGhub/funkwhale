import funkwhale_api

from funkwhale_api.common import session


def test_get_user_agent(settings):
    settings.FUNKWHALE_URL = "https://test.com"
    "http.rb/3.0.0 (Mastodon/2.2.0; +https://mastodon.eliotberriot.com/)"
    expected = "python-requests (funkwhale/{}; +{})".format(
        funkwhale_api.__version__, settings.FUNKWHALE_URL
    )
    assert session.get_user_agent() == expected


def test_get_session():
    expected = session.get_user_agent()
    assert session.get_session().headers["User-Agent"] == expected
