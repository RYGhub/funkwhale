from rest_framework_jwt import views as jwt_views

from . import serializers


class ObtainJSONWebToken(jwt_views.ObtainJSONWebToken):
    throttling_scopes = {"*": {"anonymous": "jwt-login", "authenticated": "jwt-login"}}
    serializer_class = serializers.JSONWebTokenSerializer


class RefreshJSONWebToken(jwt_views.RefreshJSONWebToken):
    throttling_scopes = {
        "*": {"anonymous": "jwt-refresh", "authenticated": "jwt-refresh"}
    }


obtain_jwt_token = ObtainJSONWebToken.as_view()
refresh_jwt_token = RefreshJSONWebToken.as_view()
