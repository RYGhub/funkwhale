import logging
import requests
import requests_http_signature

from . import exceptions
from . import utils

logger = logging.getLogger(__name__)


def verify(request, public_key):
    return requests_http_signature.HTTPSignatureAuth.verify(
        request,
        key_resolver=lambda **kwargs: public_key,
        use_auth_header=False,
    )


def verify_django(django_request, public_key):
    """
    Given a django WSGI request, create an underlying requests.PreparedRequest
    instance we can verify
    """
    headers = utils.clean_wsgi_headers(django_request.META)
    for h, v in list(headers.items()):
        # we include lower-cased version of the headers for compatibility
        # with requests_http_signature
        headers[h.lower()] = v
    try:
        signature = headers['Signature']
    except KeyError:
        raise exceptions.MissingSignature
    url = 'http://noop{}'.format(django_request.path)
    query = django_request.META['QUERY_STRING']
    if query:
        url += '?{}'.format(query)
    signature_headers = signature.split('headers="')[1].split('",')[0]
    expected = signature_headers.split(' ')
    logger.debug('Signature expected headers: %s', expected)
    for header in expected:
        try:
            headers[header]
        except KeyError:
            logger.debug('Missing header: %s', header)
    request = requests.Request(
        method=django_request.method,
        url=url,
        data=django_request.body,
        headers=headers)
    for h in request.headers.keys():
        v = request.headers[h]
        if v:
            request.headers[h] = str(v)
    prepared_request = request.prepare()
    return verify(request, public_key)
