import html
import requests

from django import http
from django.conf import settings
from django.core.cache import caches
from django import urls

from . import preferences
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

    return http.HttpResponse(head + tail)


def get_spa_html(spa_url):
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
