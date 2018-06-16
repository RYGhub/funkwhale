import requests
from django.conf import settings

import funkwhale_api


def get_user_agent():
    return "python-requests (funkwhale/{}; +{})".format(
        funkwhale_api.__version__, settings.FUNKWHALE_URL
    )


def get_session():
    s = requests.Session()
    s.headers["User-Agent"] = get_user_agent()
    return s
