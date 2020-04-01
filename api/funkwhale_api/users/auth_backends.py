from django.contrib.auth import backends, get_user_model
from allauth.account import auth_backends

from funkwhale_api.common import authentication


# ugly but allauth doesn't offer an easy way to override the querysets
# used to retrieve users, so we monkey patch
def decorate_for_auth(func):
    def inner(*args, **kwargs):
        qs = func(*args, **kwargs)
        try:
            return qs.for_auth()
        except AttributeError:
            return (
                get_user_model()
                .objects.all()
                .for_auth()
                .filter(pk__in=[u.pk for u in qs])
            )

    return inner


auth_backends.filter_users_by_email = decorate_for_auth(
    auth_backends.filter_users_by_email
)
auth_backends.filter_users_by_username = decorate_for_auth(
    auth_backends.filter_users_by_username
)


class ModelBackend(backends.ModelBackend):
    def get_user(self, user_id):
        """
        Select related to avoid two additional queries
        """
        try:
            user = get_user_model().objects.all().for_auth().get(pk=user_id)
        except get_user_model().DoesNotExist:
            return None

        return user if self.user_can_authenticate(user) else None

    def user_can_authenticate(self, user):
        can_authenticate = super().user_can_authenticate(user)
        if authentication.should_verify_email(user):
            raise authentication.UnverifiedEmail(user)

        return can_authenticate


class AllAuthBackend(auth_backends.AuthenticationBackend, ModelBackend):
    pass
