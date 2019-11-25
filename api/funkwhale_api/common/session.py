import requests
from django.conf import settings

import funkwhale_api


class FunkwhaleSession(requests.Session):
    def request(self, *args, **kwargs):
        kwargs.setdefault("verify", settings.EXTERNAL_REQUESTS_VERIFY_SSL)
        kwargs.setdefault("timeout", settings.EXTERNAL_REQUESTS_TIMEOUT)
        return super().request(*args, **kwargs)


def get_user_agent():
    return "python-requests (funkwhale/{}; +{})".format(
        funkwhale_api.__version__, settings.FUNKWHALE_URL
    )


def get_session():
    s = FunkwhaleSession()
    s.headers["User-Agent"] = get_user_agent()
    return s
