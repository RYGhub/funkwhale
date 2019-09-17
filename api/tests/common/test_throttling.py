import time
import pytest

from funkwhale_api.common import throttling


def test_get_ident_anonymous(api_request):
    ip = "92.92.92.92"
    request = api_request.get("/", HTTP_X_FORWARDED_FOR=ip)

    expected = {"id": ip, "type": "anonymous"}

    assert throttling.get_ident(request) == expected


def test_get_ident_authenticated(api_request, factories):
    user = factories["users.User"]()
    request = api_request.get("/")
    setattr(request, "user", user)
    expected = {"id": user.pk, "type": "authenticated"}
    assert throttling.get_ident(request) == expected


@pytest.mark.parametrize(
    "scope, ident, expected",
    [
        (
            "create",
            {"id": 42, "type": "authenticated"},
            "throttling:create:authenticated:42",
        ),
        (
            "list",
            {"id": "92.92.92.92", "type": "anonymous"},
            "throttling:list:anonymous:92.92.92.92",
        ),
    ],
)
def test_get_cache_key(scope, ident, expected):
    assert throttling.get_cache_key(scope, ident) == expected


@pytest.mark.parametrize(
    "action, type, view_conf, throttling_actions, expected",
    [
        # exact match, we return the rate
        ("retrieve", "anonymous", {}, {"retrieve": {"anonymous": "test"}}, "test"),
        # exact match on the view, we return the rate
        ("retrieve", "anonymous", {"retrieve": {"anonymous": "test"}}, {}, "test"),
        # no match, we return nothing
        ("retrieve", "authenticated", {}, {}, None),
        ("retrieve", "authenticated", {}, {"retrieve": {"anonymous": "test"}}, None),
        (
            "retrieve",
            "authenticated",
            {"destroy": {"authenticated": "test"}},
            {"retrieve": {"anonymous": "test"}},
            None,
        ),
        # exact match on the view, and in the settings, the view is more important
        (
            "retrieve",
            "anonymous",
            {"retrieve": {"anonymous": "test"}},
            {"retrieve": {"anonymous": "test-2"}},
            "test",
        ),
        # wildcard match, we return the wildcard value
        ("retrieve", "authenticated", {}, {"*": {"authenticated": "test"}}, "test"),
        # wildcard match, but more specific match also, we use this one instead
        (
            "retrieve",
            "authenticated",
            {},
            {"retrieve": {"authenticated": "test-2"}, "*": {"authenticated": "test"}},
            "test-2",
        ),
    ],
)
def test_get_rate_for_scope_and_ident_type(
    action, type, view_conf, throttling_actions, expected, settings
):
    settings.THROTTLING_SCOPES = throttling_actions
    assert (
        throttling.get_scope_for_action_and_ident_type(
            action=action, ident_type=type, view_conf=view_conf
        )
        is expected
    )


@pytest.mark.parametrize(
    "view_args, throttling_rates, previous_requests, expected",
    [
        # room for one more requests
        (
            {
                "action": "retrieve",
                "throttling_scopes": {"retrieve": {"anonymous": "test"}},
            },
            {"test": {"rate": "3/s"}},
            2,
            True,
        ),
        # number of requests exceeded
        (
            {
                "action": "retrieve",
                "throttling_scopes": {"retrieve": {"anonymous": "test"}},
            },
            {"test": {"rate": "3/s"}},
            3,
            False,
        ),
        # no throttling setup
        (
            {
                "action": "delete",
                "throttling_scopes": {"retrieve": {"anonymous": "test"}},
            },
            {},
            1000,
            True,
        ),
    ],
)
def test_throttle_anonymous(
    view_args,
    throttling_rates,
    previous_requests,
    expected,
    api_request,
    mocker,
    settings,
):
    settings.THROTTLING_RATES = throttling_rates
    settings.THROTTLING_SCOPES = {}
    ip = "92.92.92.92"
    ident = {"type": "anonymous", "id": ip}
    request = api_request.get("/", HTTP_X_FORWARDED_FOR=ip)

    view = mocker.Mock(**view_args)

    cache_key = throttling.get_cache_key("test", ident)
    throttle = throttling.FunkwhaleThrottle()

    history = [time.time() for _ in range(previous_requests)]
    throttle.cache.set(cache_key, history)

    assert throttle.allow_request(request, view) is expected


@pytest.mark.parametrize(
    "view_args, throttling_rates, previous_requests, expected",
    [
        # room for one more requests
        (
            {
                "action": "retrieve",
                "throttling_scopes": {"retrieve": {"authenticated": "test"}},
            },
            {"test": {"rate": "3/s"}},
            2,
            True,
        ),
        # number of requests exceeded
        (
            {
                "action": "retrieve",
                "throttling_scopes": {"retrieve": {"authenticated": "test"}},
            },
            {"test": {"rate": "3/s"}},
            3,
            False,
        ),
        # no throttling setup
        (
            {
                "action": "delete",
                "throttling_scopes": {"retrieve": {"authenticated": "test"}},
            },
            {},
            1000,
            True,
        ),
    ],
)
def test_throttle_authenticated(
    view_args,
    throttling_rates,
    previous_requests,
    expected,
    api_request,
    mocker,
    settings,
    factories,
):
    settings.THROTTLING_RATES = throttling_rates
    settings.THROTTLING_SCOPES = {}
    user = factories["users.User"]()
    ident = {"type": "authenticated", "id": user.pk}
    request = api_request.get("/")
    setattr(request, "user", user)

    view = mocker.Mock(**view_args)

    cache_key = throttling.get_cache_key("test", ident)
    throttle = throttling.FunkwhaleThrottle()

    history = [time.time() for _ in range(previous_requests)]
    throttle.cache.set(cache_key, history)

    assert throttle.allow_request(request, view) is expected


def throttle_successive(settings, mocker, api_request):
    settings.THROTTLING_RATES = {"test": {"rate": "3/s"}}
    settings.THROTTLING_SCOPES = {}
    ip = "92.92.92.92"
    request = api_request.get("/", HTTP_X_FORWARDED_FOR=ip)

    view = mocker.Mock(
        action="retrieve", throttling_scopes={"retrieve": {"anonymous": "test"}}
    )

    throttle = throttling.FunkwhaleThrottle()

    assert throttle.allow_request(request, view) is True
    assert throttle.allow_request(request, view) is True
    assert throttle.allow_request(request, view) is True
    assert throttle.allow_request(request, view) is False


def test_throttle_attach_info(mocker):
    throttle = throttling.FunkwhaleThrottle()
    request = mocker.Mock()
    setattr(throttle, "num_requests", 300)
    setattr(throttle, "duration", 3600)
    setattr(throttle, "scope", "hello")
    setattr(throttle, "history", [])
    setattr(throttle, "request", request)

    expected = {
        "num_requests": throttle.num_requests,
        "duration": throttle.duration,
        "history": throttle.history,
        "wait": throttle.wait(),
        "scope": throttle.scope,
    }
    throttle.attach_info()

    assert request._throttle_status == expected


@pytest.mark.parametrize("method", ["throttle_success", "throttle_failure"])
def test_throttle_calls_attach_info(method, mocker):
    throttle = throttling.FunkwhaleThrottle()
    setattr(throttle, "key", "noop")
    setattr(throttle, "now", "noop")
    setattr(throttle, "duration", "noop")
    setattr(throttle, "history", ["noop"])
    mocker.patch.object(throttle, "cache")
    attach_info = mocker.patch.object(throttle, "attach_info")
    func = getattr(throttle, method)

    func()

    attach_info.assert_called_once_with()


def test_allow_request(api_request, settings, mocker):
    settings.THROTTLING_RATES = {"test": {"rate": "2/s"}}
    ip = "92.92.92.92"
    request = api_request.get("/", HTTP_X_FORWARDED_FOR=ip)
    allow_request = mocker.spy(throttling.FunkwhaleThrottle, "allow_request")
    action = "test"
    throttling_scopes = {"test": {"anonymous": "test", "authenticated": "test"}}
    throttling.check_request(request, action)
    throttling.check_request(request, action)
    with pytest.raises(throttling.TooManyRequests):
        throttling.check_request(request, action)

    assert allow_request.call_count == 3
    assert allow_request.call_args[0][1] == request
    assert allow_request.call_args[0][2] == throttling.DummyView(
        action=action, throttling_scopes=throttling_scopes
    )


def test_allow_request_throttling_disabled(api_request, settings):
    settings.THROTTLING_RATES = {"test": {"rate": "1/s"}}
    settings.THROTTLING_ENABLED = False
    ip = "92.92.92.92"
    request = api_request.get("/", HTTP_X_FORWARDED_FOR=ip)
    action = "test"
    throttling.check_request(request, action)
    # even exceeding request doesn't raise any exception
    throttling.check_request(request, action)


def test_get_throttling_status_for_ident(settings, cache):
    settings.THROTTLING_RATES = {
        "test-1": {"rate": "30/d", "description": "description 1"},
        "test-2": {"rate": "20/h", "description": "description 2"},
    }
    ident = {"type": "anonymous", "id": "92.92.92.92"}
    test1_cache_key = throttling.get_cache_key("test-1", ident)
    now = int(time.time())
    cache.set(test1_cache_key, [now - 1, now - 2, now - 99999999])

    expected = [
        {
            "id": "test-1",
            "limit": 30,
            "rate": "30/d",
            "description": "description 1",
            "duration": 24 * 3600,
            "remaining": 28,
            "reset": now + (24 * 3600) - 1,
            "reset_seconds": (24 * 3600) - 1,
            "available": None,
            "available_seconds": None,
        },
        {
            "id": "test-2",
            "limit": 20,
            "rate": "20/h",
            "description": "description 2",
            "duration": 3600,
            "remaining": 20,
            "reset": None,
            "reset_seconds": None,
            "available": None,
            "available_seconds": None,
        },
    ]
    assert throttling.get_status(ident, now) == expected
