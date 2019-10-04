from django.conf.urls import url
from django.views.generic import TemplateView
from rest_auth import views as rest_auth_views

from . import views

urlpatterns = [
    # URLs that do not require a session or valid token
    url(
        r"^password/reset/$",
        views.PasswordResetView.as_view(),
        name="rest_password_reset",
    ),
    url(
        r"^password/reset/confirm/$",
        views.PasswordResetConfirmView.as_view(),
        name="rest_password_reset_confirm",
    ),
    # URLs that require a user to be logged in with a valid session / token.
    url(
        r"^user/$", rest_auth_views.UserDetailsView.as_view(), name="rest_user_details"
    ),
    url(
        r"^password/change/$",
        views.PasswordChangeView.as_view(),
        name="rest_password_change",
    ),
    # Registration URLs
    url(r"^registration/$", views.RegisterView.as_view(), name="rest_register"),
    url(
        r"^registration/verify-email/?$",
        views.VerifyEmailView.as_view(),
        name="rest_verify_email",
    ),
    url(
        r"^registration/change-password/?$",
        views.PasswordChangeView.as_view(),
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
        r"^registration/account-confirm-email/(?P<key>\w+)/?$",
        TemplateView.as_view(),
        name="account_confirm_email",
    ),
]
