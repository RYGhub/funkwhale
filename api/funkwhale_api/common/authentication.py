from rest_framework import exceptions
from rest_framework_jwt import authentication
from rest_framework_jwt.settings import api_settings


class JSONWebTokenAuthenticationQS(
        authentication.BaseJSONWebTokenAuthentication):

    www_authenticate_realm = 'api'

    def get_jwt_value(self, request):
        token = request.query_params.get('jwt')
        if 'jwt' in request.query_params and not token:
            msg = _('Invalid Authorization header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        return token

    def authenticate_header(self, request):
        return '{0} realm="{1}"'.format(
            api_settings.JWT_AUTH_HEADER_PREFIX, self.www_authenticate_realm)
