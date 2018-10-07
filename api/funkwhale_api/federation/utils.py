import unicodedata
import re
from django.conf import settings

from funkwhale_api.common import session

from . import signing


def full_url(path):
    """
    Given a relative path, return a full url usable for federation purpose
    """
    if path.startswith("http://") or path.startswith("https://"):
        return path
    root = settings.FUNKWHALE_URL
    if path.startswith("/") and root.endswith("/"):
        return root + path[1:]
    elif not path.startswith("/") and not root.endswith("/"):
        return root + "/" + path
    else:
        return root + path


def clean_wsgi_headers(raw_headers):
    """
    Convert WSGI headers from CONTENT_TYPE to Content-Type notation
    """
    cleaned = {}
    non_prefixed = ["content_type", "content_length"]
    for raw_header, value in raw_headers.items():
        h = raw_header.lower()
        if not h.startswith("http_") and h not in non_prefixed:
            continue

        words = h.replace("http_", "", 1).split("_")
        cleaned_header = "-".join([w.capitalize() for w in words])
        cleaned[cleaned_header] = value

    return cleaned


def slugify_username(username):
    """
    Given a username such as "hello M. world", returns a username
    suitable for federation purpose (hello_M_world).

    Preserves the original case.

    Code is borrowed from django's slugify function.
    """

    value = str(username)
    value = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
    value = re.sub(r"[^\w\s-]", "", value).strip()
    return re.sub(r"[-\s]+", "_", value)


def retrieve(fid, actor=None, serializer_class=None, queryset=None):
    if queryset:
        try:
            # queryset can also be a Model class
            existing = queryset.filter(fid=fid).first()
        except AttributeError:
            existing = queryset.objects.filter(fid=fid).first()
        if existing:
            return existing

    auth = (
        None if not actor else signing.get_auth(actor.private_key, actor.private_key_id)
    )
    response = session.get_session().get(
        fid,
        auth=auth,
        timeout=5,
        verify=settings.EXTERNAL_REQUESTS_VERIFY_SSL,
        headers={
            "Accept": "application/activity+json",
            "Content-Type": "application/activity+json",
        },
    )
    response.raise_for_status()
    data = response.json()
    if not serializer_class:
        return data
    serializer = serializer_class(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.save()
