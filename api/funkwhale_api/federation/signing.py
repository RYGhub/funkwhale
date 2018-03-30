import requests
import requests_http_signature


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
    headers = django_request.META.get('headers', {}).copy()
    for h, v in list(headers.items()):
        # we include lower-cased version of the headers for compatibility
        # with requests_http_signature
        headers[h.lower()] = v
    try:
        signature = headers['signature']
    except KeyError:
        raise exceptions.MissingSignature

    request = requests.Request(
        method=django_request.method,
        url='http://noop',
        data=django_request.body,
        headers=headers)

    prepared_request = request.prepare()
    return verify(request, public_key)
