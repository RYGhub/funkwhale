from django.contrib import auth

from rest_framework import response
from rest_framework import views

from . import auth_serializers


class LoginView(views.APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):

        serializer = auth_serializers.LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        auth.login(request=request, user=serializer.validated_data["user"])

        payload = {}

        return response.Response(payload)


class LogoutView(views.APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        auth.logout(request)
        payload = {}
        return response.Response(payload)
