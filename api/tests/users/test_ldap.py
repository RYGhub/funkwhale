from django.contrib.auth import get_backends

from django_auth_ldap import backend


def test_ldap_user_creation_also_creates_actor(settings, factories, mocker):
    actor = factories["federation.Actor"]()
    mocker.patch("funkwhale_api.users.models.create_actor", return_value=actor)
    mocker.patch(
        "django_auth_ldap.backend.LDAPBackend.ldap_to_django_username",
        return_value="hello",
    )
    settings.AUTHENTICATION_BACKENDS += ("django_auth_ldap.backend.LDAPBackend",)
    # django-auth-ldap offers a populate_user signal we can use
    # to create our user actor if it does not exists
    ldap_backend = get_backends()[-1]
    ldap_user = backend._LDAPUser(ldap_backend, username="hello")
    ldap_user._user_attrs = {"hello": "world"}
    ldap_user._get_or_create_user()
    ldap_user._user.refresh_from_db()

    assert ldap_user._user.actor == actor
