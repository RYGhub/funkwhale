import pytest

from funkwhale_api.common import middleware


def test_spa_fallback_middleware_no_404(mocker):
    get_response = mocker.Mock()
    get_response.return_value = mocker.Mock(status_code=200)
    request = mocker.Mock(path="/")
    m = middleware.SPAFallbackMiddleware(get_response)

    assert m(request) == get_response.return_value


def test_spa_middleware_calls_should_fallback_false(mocker):
    get_response = mocker.Mock()
    get_response.return_value = mocker.Mock(status_code=404)
    should_falback = mocker.patch.object(
        middleware, "should_fallback_to_spa", return_value=False
    )
    request = mocker.Mock(path="/")

    m = middleware.SPAFallbackMiddleware(get_response)

    assert m(request) == get_response.return_value
    should_falback.assert_called_once_with(request.path)


def test_spa_middleware_should_fallback_true(mocker):
    get_response = mocker.Mock()
    get_response.return_value = mocker.Mock(status_code=404)
    request = mocker.Mock(path="/")
    mocker.patch.object(middleware, "should_fallback_to_spa", return_value=True)
    serve_spa = mocker.patch.object(middleware, "serve_spa")
    m = middleware.SPAFallbackMiddleware(get_response)

    assert m(request) == serve_spa.return_value
    serve_spa.assert_called_once_with(request)


@pytest.mark.parametrize(
    "path,expected",
    [("/", True), ("/federation", False), ("/api", False), ("/an/spa/path/", True)],
)
def test_should_fallback(path, expected, mocker):
    assert middleware.should_fallback_to_spa(path) is expected


def test_serve_spa_from_cache(mocker, settings, preferences, no_api_auth):

    request = mocker.Mock(path="/")
    get_spa_html = mocker.patch.object(
        middleware, "get_spa_html", return_value="<html><head></head></html>"
    )
    mocker.patch.object(
        middleware,
        "get_default_head_tags",
        return_value=[
            {"tag": "meta", "property": "og:title", "content": "default title"},
            {"tag": "meta", "property": "og:site_name", "content": "default site name"},
        ],
    )
    get_request_head_tags = mocker.patch.object(
        middleware,
        "get_request_head_tags",
        return_value=[
            {"tag": "meta", "property": "og:title", "content": "custom title"},
            {
                "tag": "meta",
                "property": "og:description",
                "content": "custom description",
            },
        ],
    )
    response = middleware.serve_spa(request)

    assert response.status_code == 200
    expected = [
        "<html><head>",
        '<meta content="custom title" property="og:title" />',
        '<meta content="custom description" property="og:description" />',
        '<meta content="default site name" property="og:site_name" />',
        "</head></html>",
    ]
    get_spa_html.assert_called_once_with(settings.FUNKWHALE_SPA_HTML_ROOT)
    get_request_head_tags.assert_called_once_with(request)
    assert response.content == "\n".join(expected).encode()


def test_get_default_head_tags(preferences, settings):
    settings.APP_NAME = "Funkwhale"
    preferences["instance__name"] = "Hello"
    preferences["instance__short_description"] = "World"

    expected = [
        {"tag": "meta", "property": "og:type", "content": "website"},
        {"tag": "meta", "property": "og:site_name", "content": "Hello - Funkwhale"},
        {"tag": "meta", "property": "og:description", "content": "World"},
        {
            "tag": "meta",
            "property": "og:image",
            "content": settings.FUNKWHALE_URL + "/front/favicon.png",
        },
        {"tag": "meta", "property": "og:url", "content": settings.FUNKWHALE_URL + "/"},
    ]

    assert middleware.get_default_head_tags("/") == expected


def test_get_spa_html_from_cache(local_cache):
    local_cache.set("spa-html:http://test", "hello world")

    assert middleware.get_spa_html("http://test") == "hello world"


def test_get_spa_html_from_http(local_cache, r_mock, mocker, settings):
    cache_set = mocker.spy(local_cache, "set")
    url = "http://test"
    r_mock.get(url + "/index.html", text="hello world")

    assert middleware.get_spa_html("http://test") == "hello world"
    cache_set.assert_called_once_with(
        "spa-html:{}".format(url),
        "hello world",
        settings.FUNKWHALE_SPA_HTML_CACHE_DURATION,
    )


def test_get_route_head_tags(mocker, settings):
    match = mocker.Mock(args=[], kwargs={"pk": 42}, func=mocker.Mock())
    resolve = mocker.patch("django.urls.resolve", return_value=match)
    request = mocker.Mock(path="/tracks/42")
    tags = middleware.get_request_head_tags(request)

    assert tags == match.func.return_value
    match.func.assert_called_once_with(request, *[], **{"pk": 42})
    resolve.assert_called_once_with(request.path, urlconf=settings.SPA_URLCONF)