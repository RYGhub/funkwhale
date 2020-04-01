from django.conf import settings
from django.utils.encoding import smart_text
from django.utils.translation import ugettext as _
from rest_framework import exceptions
from rest_framework_jwt import authentication
from rest_framework_jwt.settings import api_settings


def should_verify_email(user):
    if user.is_superuser:
        return False
    has_unverified_email = not user.has_verified_primary_email
    mandatory_verification = settings.ACCOUNT_EMAIL_VERIFICATION != "optional"
    return has_unverified_email and mandatory_verification


class BaseJsonWebTokenAuth(object):
    def authenticate_credentials(self, payload):
        """
        We have to implement this method by hand to ensure we can check that the
        User has a verified email, if required
        """
        User = authentication.get_user_model()
        username = authentication.jwt_get_username_from_payload(payload)

        if not username:
            msg = _("Invalid payload.")
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            msg = _("Invalid signature.")
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = _("User account is disabled.")
            raise exceptions.AuthenticationFailed(msg)

        if should_verify_email(user):

            msg = _("You need to verify your email address.")
            raise exceptions.AuthenticationFailed(msg)

        return user


class JSONWebTokenAuthenticationQS(
    BaseJsonWebTokenAuth, authentication.BaseJSONWebTokenAuthentication
):

    www_authenticate_realm = "api"

    def get_jwt_value(self, request):
        token = request.query_params.get("jwt")
        if "jwt" in request.query_params and not token:
            msg = _("Invalid Authorization header. No credentials provided.")
            raise exceptions.AuthenticationFailed(msg)
        return token

    def authenticate_header(self, request):
        return '{0} realm="{1}"'.format(
            api_settings.JWT_AUTH_HEADER_PREFIX, self.www_authenticate_realm
        )


class BearerTokenHeaderAuth(
    BaseJsonWebTokenAuth, authentication.BaseJSONWebTokenAuthentication
):
    """
    For backward compatibility purpose, we used Authorization: JWT <token>
    but Authorization: Bearer <token> is probably better.
    """

    www_authenticate_realm = "api"

    def get_jwt_value(self, request):
        auth = authentication.get_authorization_header(request).split()
        auth_header_prefix = "bearer"

        if not auth:
            if api_settings.JWT_AUTH_COOKIE:
                return request.COOKIES.get(api_settings.JWT_AUTH_COOKIE)
            return None

        if smart_text(auth[0].lower()) != auth_header_prefix:
            return None

        if len(auth) == 1:
            msg = _("Invalid Authorization header. No credentials provided.")
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _(
                "Invalid Authorization header. Credentials string "
                "should not contain spaces."
            )
            raise exceptions.AuthenticationFailed(msg)

        return auth[1]

    def authenticate_header(self, request):
        return '{0} realm="{1}"'.format("Bearer", self.www_authenticate_realm)

    def authenticate(self, request):
        auth = super().authenticate(request)
        if auth:
            if not auth[0].actor:
                auth[0].create_actor()
        return auth


class JSONWebTokenAuthentication(
    BaseJsonWebTokenAuth, authentication.JSONWebTokenAuthentication
):
    def authenticate(self, request):
        auth = super().authenticate(request)

        if auth:
            if not auth[0].actor:
                auth[0].create_actor()
        return auth
