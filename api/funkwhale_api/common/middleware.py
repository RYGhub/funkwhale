import html
import requests
import time
import xml.sax.saxutils

from django import http
from django.conf import settings
from django.core.cache import caches
from django import urls
from rest_framework import views

from . import preferences
from . import throttling
from . import utils

EXCLUDED_PATHS = ["/api", "/federation", "/.well-known"]


def should_fallback_to_spa(path):
    if path == "/":
        return True
    return not any([path.startswith(m) for m in EXCLUDED_PATHS])


def serve_spa(request):
    html = get_spa_html(settings.FUNKWHALE_SPA_HTML_ROOT)
    head, tail = html.split("</head>", 1)
    if not preferences.get("common__api_authentication_required"):
        try:
            request_tags = get_request_head_tags(request) or []
        except urls.exceptions.Resolver404:
            # we don't have any custom tags for this route
            request_tags = []
    else:
        # API is not open, we don't expose any custom data
        request_tags = []
    default_tags = get_default_head_tags(request.path)
    unique_attributes = ["name", "property"]

    final_tags = request_tags
    skip = []

    for t in final_tags:
        for attr in unique_attributes:
            if attr in t:
                skip.append(t[attr])
    for t in default_tags:
        existing = False
        for attr in unique_attributes:
            if t.get(attr) in skip:
                existing = True
                break
        if not existing:
            final_tags.append(t)

    # let's inject our meta tags in the HTML
    head += "\n" + "\n".join(render_tags(final_tags)) + "\n</head>"
    css = get_custom_css() or ""
    if css:
        # We add the style add the end of the body to ensure it has the highest
        # priority (since it will come after other stylesheets)
        body, tail = tail.split("</body>", 1)
        css = "<style>{}</style>".format(css)
        tail = body + "\n" + css + "\n</body>" + tail
    return http.HttpResponse(head + tail)


def get_spa_html(spa_url):
    if spa_url.startswith("/"):
        # we try to open a local file
        with open(spa_url) as f:
            return f.read()
    cache_key = "spa-html:{}".format(spa_url)
    cached = caches["local"].get(cache_key)
    if cached:
        return cached

    response = requests.get(
        utils.join_url(spa_url, "index.html"),
        verify=settings.EXTERNAL_REQUESTS_VERIFY_SSL,
    )
    response.raise_for_status()
    content = response.text
    caches["local"].set(cache_key, content, settings.FUNKWHALE_SPA_HTML_CACHE_DURATION)
    return content


def get_default_head_tags(path):
    instance_name = preferences.get("instance__name")
    short_description = preferences.get("instance__short_description")
    app_name = settings.APP_NAME

    parts = [instance_name, app_name]

    return [
        {"tag": "meta", "property": "og:type", "content": "website"},
        {
            "tag": "meta",
            "property": "og:site_name",
            "content": " - ".join([p for p in parts if p]),
        },
        {"tag": "meta", "property": "og:description", "content": short_description},
        {
            "tag": "meta",
            "property": "og:image",
            "content": utils.join_url(settings.FUNKWHALE_URL, "/front/favicon.png"),
        },
        {
            "tag": "meta",
            "property": "og:url",
            "content": utils.join_url(settings.FUNKWHALE_URL, path),
        },
    ]


def render_tags(tags):
    """
    Given a dict like {'tag': 'meta', 'hello': 'world'}
    return a html ready tag like
    <meta hello="world" />
    """
    for tag in tags:

        yield "<{tag} {attrs} />".format(
            tag=tag.pop("tag"),
            attrs=" ".join(
                [
                    '{}="{}"'.format(a, html.escape(str(v)))
                    for a, v in sorted(tag.items())
                    if v
                ]
            ),
        )


def get_request_head_tags(request):
    match = urls.resolve(request.path, urlconf=settings.SPA_URLCONF)
    return match.func(request, *match.args, **match.kwargs)


def get_custom_css():
    css = preferences.get("ui__custom_css").strip()
    if not css:
        return

    return xml.sax.saxutils.escape(css)


class SPAFallbackMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if response.status_code == 404 and should_fallback_to_spa(request.path):
            return serve_spa(request)

        return response


class DevHttpsMiddleware:
    """
    In development, it's sometimes difficult to have django use HTTPS
    when we have django behind nginx behind traefix.

    We thus use a simple setting (in dev ONLY) to control that.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.FORCE_HTTPS_URLS:
            setattr(request.__class__, "scheme", "https")
            setattr(
                request,
                "get_host",
                lambda: request.__class__.get_host(request).replace(":80", ":443"),
            )
        return self.get_response(request)


def monkey_patch_rest_initialize_request():
    """
    Rest framework use it's own APIRequest, meaning we can't easily
    access our throttling info in the middleware. So me monkey patch the
    `initialize_request` method from rest_framework to keep a link between both requests
    """
    original = views.APIView.initialize_request

    def replacement(self, request, *args, **kwargs):
        r = original(self, request, *args, **kwargs)
        setattr(request, "_api_request", r)
        return r

    setattr(views.APIView, "initialize_request", replacement)


monkey_patch_rest_initialize_request()


class ThrottleStatusMiddleware:
    """
    Include useful information regarding throttling in API responses to
    ensure clients can adapt.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except throttling.TooManyRequests:
            # manual throttling in non rest_framework view, we have to return
            # the proper response ourselves
            response = http.HttpResponse(status=429)
        request_to_check = request
        try:
            request_to_check = request._api_request
        except AttributeError:
            pass
        throttle_status = getattr(request_to_check, "_throttle_status", None)
        if throttle_status:
            response["X-RateLimit-Limit"] = str(throttle_status["num_requests"])
            response["X-RateLimit-Scope"] = str(throttle_status["scope"])
            response["X-RateLimit-Remaining"] = throttle_status["num_requests"] - len(
                throttle_status["history"]
            )
            response["X-RateLimit-Duration"] = str(throttle_status["duration"])
            if throttle_status["history"]:
                now = int(time.time())
                # At this point, the client can send additional requests
                oldtest_request = throttle_status["history"][-1]
                remaining = throttle_status["duration"] - (now - int(oldtest_request))
                response["Retry-After"] = str(remaining)
                # At this point, all Rate Limit is reset to 0
                latest_request = throttle_status["history"][0]
                remaining = throttle_status["duration"] - (now - int(latest_request))
                response["X-RateLimit-Reset"] = str(now + remaining)
                response["X-RateLimit-ResetSeconds"] = str(remaining)

        return response
