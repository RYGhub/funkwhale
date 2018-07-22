from django.conf import settings


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
