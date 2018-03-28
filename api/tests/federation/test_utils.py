import pytest

from funkwhale_api.federation import utils


@pytest.mark.parametrize('url,path,expected', [
    ('http://test.com', '/hello', 'http://test.com/hello'),
    ('http://test.com/', 'hello', 'http://test.com/hello'),
    ('http://test.com/', '/hello', 'http://test.com/hello'),
    ('http://test.com', 'hello', 'http://test.com/hello'),
])
def test_full_url(settings, url, path, expected):
    settings.FUNKWHALE_URL = url
    assert utils.full_url(path) == expected
