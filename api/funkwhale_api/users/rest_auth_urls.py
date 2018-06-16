from django.conf.urls import url
from django.views.generic import TemplateView
from rest_auth import views as rest_auth_views
from rest_auth.registration import views as registration_views

from . import views

urlpatterns = [
    url(r"^$", views.RegisterView.as_view(), name="rest_register"),
    url(
        r"^verify-email/$",
        registration_views.VerifyEmailView.as_view(),
        name="rest_verify_email",
    ),
    url(
        r"^change-password/$",
        rest_auth_views.PasswordChangeView.as_view(),
        name="change_password",
    ),
    # This url is used by django-allauth and empty TemplateView is
    # defined just to allow reverse() call inside app, for example when email
    # with verification link is being sent, then it's required to render email
    # content.
    # account_confirm_email - You should override this view to handle it in
    # your API client somehow and then, send post to /verify-email/ endpoint
    # with proper key.
    # If you don't want to use API on that step, then just use ConfirmEmailView
    # view from:
    # djang-allauth https://github.com/pennersr/django-allauth/blob/master/allauth/account/views.py#L190
    url(
        r"^account-confirm-email/(?P<key>\w+)/$",
        TemplateView.as_view(),
        name="account_confirm_email",
    ),
]
