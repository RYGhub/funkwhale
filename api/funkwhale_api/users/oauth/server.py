import urllib.parse
import oauthlib.oauth2

from funkwhale_api.common import authentication


def check(request):
    user = request.user
    request.user = user.__class__.objects.all().for_auth().get(pk=user.pk)
    if authentication.should_verify_email(request.user):
        raise authentication.UnverifiedEmail(user)
    return True


class OAuth2Server(oauthlib.oauth2.Server):
    def verify_request(self, uri, *args, **kwargs):
        valid, request = super().verify_request(uri, *args, **kwargs)
        if valid:
            if not check(request):
                return False, request
            return valid, request

        # maybe the token was given in the querystring?
        query = urllib.parse.urlparse(request.uri).query
        token = None
        if query:
            parsed_qs = urllib.parse.parse_qs(query)
            token = parsed_qs.get("token", [])
            if len(token) > 0:
                token = token[0]

        if token:
            valid = self.request_validator.validate_bearer_token(
                token, request.scopes, request
            )
        if valid:
            if not check(request):
                return False, request

        return valid, request
