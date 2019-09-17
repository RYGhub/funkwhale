import collections

from django.core.cache import cache
from rest_framework import throttling as rest_throttling

from django.conf import settings


def get_ident(request):
    if hasattr(request, "user") and request.user.is_authenticated:
        return {"type": "authenticated", "id": request.user.pk}
    ident = rest_throttling.BaseThrottle().get_ident(request)

    return {"type": "anonymous", "id": ident}


def get_cache_key(scope, ident):
    parts = ["throttling", scope, ident["type"], str(ident["id"])]
    return ":".join(parts)


def get_scope_for_action_and_ident_type(action, ident_type, view_conf={}):
    config = collections.ChainMap(view_conf, settings.THROTTLING_SCOPES)

    try:
        action_config = config[action]
    except KeyError:
        action_config = config.get("*", {})

    try:
        return action_config[ident_type]
    except KeyError:
        return


def get_status(ident, now):
    data = []
    throttle = FunkwhaleThrottle()
    for key in sorted(settings.THROTTLING_RATES.keys()):
        conf = settings.THROTTLING_RATES[key]
        row_data = {"id": key, "rate": conf["rate"], "description": conf["description"]}
        if conf["rate"]:
            num_requests, duration = throttle.parse_rate(conf["rate"])
            history = cache.get(get_cache_key(key, ident)) or []

            relevant_history = [h for h in history if h > now - duration]
            row_data["limit"] = num_requests
            row_data["duration"] = duration
            row_data["remaining"] = num_requests - len(relevant_history)
            if relevant_history and len(relevant_history) >= num_requests:
                # At this point, the endpoint becomes available again
                now_request = relevant_history[-1]
                remaining = duration - (now - int(now_request))
                row_data["available"] = int(now + remaining) or None
                row_data["available_seconds"] = int(remaining) or None
            else:
                row_data["available"] = None
                row_data["available_seconds"] = None

            if relevant_history:
                # At this point, all Rate Limit is reset to 0
                latest_request = relevant_history[0]
                remaining = duration - (now - int(latest_request))
                row_data["reset"] = int(now + remaining)
                row_data["reset_seconds"] = int(remaining)
            else:
                row_data["reset"] = None
                row_data["reset_seconds"] = None
        else:
            row_data["limit"] = None
            row_data["duration"] = None
            row_data["remaining"] = None
            row_data["available"] = None
            row_data["available_seconds"] = None
            row_data["reset"] = None
            row_data["reset_seconds"] = None

        data.append(row_data)

    return data


class FunkwhaleThrottle(rest_throttling.SimpleRateThrottle):
    def __init__(self):
        pass

    def get_cache_key(self, request, view):
        return get_cache_key(self.scope, self.ident)

    def allow_request(self, request, view):
        self.request = request
        self.ident = get_ident(request)
        action = getattr(view, "action", "*")
        view_scopes = getattr(view, "throttling_scopes", {})
        if view_scopes is None:
            return True
        self.scope = get_scope_for_action_and_ident_type(
            action=action, ident_type=self.ident["type"], view_conf=view_scopes
        )
        if not self.scope or self.scope not in settings.THROTTLING_RATES:
            return True
        self.rate = settings.THROTTLING_RATES[self.scope].get("rate")
        self.num_requests, self.duration = self.parse_rate(self.rate)
        self.request = request

        return super().allow_request(request, view)

    def attach_info(self):
        info = {
            "num_requests": self.num_requests,
            "duration": self.duration,
            "scope": self.scope,
            "history": self.history or [],
            "wait": self.wait(),
        }
        setattr(self.request, "_throttle_status", info)

    def throttle_success(self):
        self.attach_info()
        return super().throttle_success()

    def throttle_failure(self):
        self.attach_info()
        return super().throttle_failure()


class TooManyRequests(Exception):
    pass


DummyView = collections.namedtuple("DummyView", "action throttling_scopes")


def check_request(request, scope):
    """
    A simple wrapper around FunkwhaleThrottle for views that aren't API views
    or cannot use rest_framework automatic throttling.

    Raise TooManyRequests if limit is reached.
    """
    if not settings.THROTTLING_ENABLED:
        return True

    view = DummyView(
        action=scope,
        throttling_scopes={scope: {"anonymous": scope, "authenticated": scope}},
    )
    throttle = FunkwhaleThrottle()
    if not throttle.allow_request(request, view):
        raise TooManyRequests()
    return True
