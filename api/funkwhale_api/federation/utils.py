from django.conf import settings


def full_url(path):
    """
    Given a relative path, return a full url usable for federation purpose
    """
    root = settings.FUNKWHALE_URL
    if path.startswith('/') and root.endswith('/'):
        return root + path[1:]
    elif not path.startswith('/') and not root.endswith('/'):
        return root + '/' + path
    else:
        return root + path
