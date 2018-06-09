import pytest

from funkwhale_api.federation import utils


@pytest.mark.parametrize(
    "url,path,expected",
    [
        ("http://test.com", "/hello", "http://test.com/hello"),
        ("http://test.com/", "hello", "http://test.com/hello"),
        ("http://test.com/", "/hello", "http://test.com/hello"),
        ("http://test.com", "hello", "http://test.com/hello"),
    ],
)
def test_full_url(settings, url, path, expected):
    settings.FUNKWHALE_URL = url
    assert utils.full_url(path) == expected


def test_extract_headers_from_meta():
    wsgi_headers = {
        "HTTP_HOST": "nginx",
        "HTTP_X_REAL_IP": "172.20.0.4",
        "HTTP_X_FORWARDED_FOR": "188.165.228.227, 172.20.0.4",
        "HTTP_X_FORWARDED_PROTO": "http",
        "HTTP_X_FORWARDED_HOST": "localhost:80",
        "HTTP_X_FORWARDED_PORT": "80",
        "HTTP_CONNECTION": "close",
        "CONTENT_LENGTH": "1155",
        "CONTENT_TYPE": "txt/application",
        "HTTP_SIGNATURE": "Hello",
        "HTTP_DATE": "Sat, 31 Mar 2018 13:53:55 GMT",
        "HTTP_USER_AGENT": "http.rb/3.0.0 (Mastodon/2.2.0; +https://mastodon.eliotberriot.com/)",
    }

    cleaned_headers = utils.clean_wsgi_headers(wsgi_headers)

    expected = {
        "Host": "nginx",
        "X-Real-Ip": "172.20.0.4",
        "X-Forwarded-For": "188.165.228.227, 172.20.0.4",
        "X-Forwarded-Proto": "http",
        "X-Forwarded-Host": "localhost:80",
        "X-Forwarded-Port": "80",
        "Connection": "close",
        "Content-Length": "1155",
        "Content-Type": "txt/application",
        "Signature": "Hello",
        "Date": "Sat, 31 Mar 2018 13:53:55 GMT",
        "User-Agent": "http.rb/3.0.0 (Mastodon/2.2.0; +https://mastodon.eliotberriot.com/)",
    }
    assert cleaned_headers == expected
