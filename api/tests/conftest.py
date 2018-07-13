import datetime
import io
import PIL
import random
import shutil
import tempfile

import factory
import pytest
import requests_mock
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache as django_cache
from django.utils import timezone
from django.test import client
from dynamic_preferences.registries import global_preferences_registry
from rest_framework import fields as rest_fields
from rest_framework.test import APIClient, APIRequestFactory

from funkwhale_api.activity import record
from funkwhale_api.users.permissions import HasUserPermission


@pytest.fixture(scope="session", autouse=True)
def factories_autodiscover():
    from django.apps import apps
    from funkwhale_api import factories

    app_names = [app.name for app in apps.app_configs.values()]
    factories.registry.autodiscover(app_names)


@pytest.fixture(autouse=True)
def cache():
    """
    Returns a django Cache instance for cache-related operations
    """
    yield django_cache
    django_cache.clear()


@pytest.fixture
def factories(db):
    """
    Returns a dictionnary containing all registered factories with keys such as
    users.User or music.Track
    """
    from funkwhale_api import factories

    for v in factories.registry.values():
        try:
            v._meta.strategy = factory.CREATE_STRATEGY
        except AttributeError:
            # probably not a class based factory
            pass
    yield factories.registry


@pytest.fixture
def nodb_factories():
    """
    Returns a dictionnary containing all registered factories with a build strategy
    that does not require access to the database
    """
    from funkwhale_api import factories

    for v in factories.registry.values():
        try:
            v._meta.strategy = factory.BUILD_STRATEGY
        except AttributeError:
            # probably not a class based factory
            pass
    yield factories.registry


@pytest.fixture
def preferences(db, cache):
    """
    return a dynamic_preferences manager for global_preferences
    """
    manager = global_preferences_registry.manager()
    manager.all()
    yield manager


@pytest.fixture
def tmpdir():
    """
    Returns a temporary directory path where you can write things during your
    test
    """
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)


@pytest.fixture
def tmpfile():
    """
    Returns a temporary file where you can write things during your test
    """
    yield tempfile.NamedTemporaryFile()


@pytest.fixture
def logged_in_client(db, factories, client):
    """
    Returns a logged-in, non-API client with an authenticated ``User``
    stored in the ``user`` attribute
    """
    user = factories["users.User"]()
    assert client.login(username=user.username, password="test")
    setattr(client, "user", user)
    yield client
    delattr(client, "user")


@pytest.fixture
def anonymous_user():
    """Returns a AnonymousUser() instance"""
    return AnonymousUser()


@pytest.fixture
def api_client(client):
    """
    Return an API client without any authentication
    """
    return APIClient()


@pytest.fixture
def logged_in_api_client(db, factories, api_client):
    """
    Return a logged-in API client with an authenticated ``User``
    stored in the ``user`` attribute
    """
    user = factories["users.User"]()
    assert api_client.login(username=user.username, password="test")
    api_client.force_authenticate(user=user)
    setattr(api_client, "user", user)
    yield api_client
    delattr(api_client, "user")


@pytest.fixture
def superuser_api_client(db, factories, api_client):
    """
    Return a logged-in API client with an authenticated superuser
    stored in the ``user`` attribute
    """
    user = factories["users.SuperUser"]()
    assert api_client.login(username=user.username, password="test")
    setattr(api_client, "user", user)
    yield api_client
    delattr(api_client, "user")


@pytest.fixture
def superuser_client(db, factories, client):
    """
    Return a logged-in, non-API client with an authenticated ``User``
    stored in the ``user`` attribute
    """
    user = factories["users.SuperUser"]()
    assert client.login(username=user.username, password="test")
    setattr(client, "user", user)
    yield client
    delattr(client, "user")


@pytest.fixture
def api_request():
    """
    Returns a dummy API request object you can pass to API views
    """
    return APIRequestFactory()


@pytest.fixture
def fake_request():
    """
    Returns a dummy, non-API request object you can pass to regular views
    """
    return client.RequestFactory()


@pytest.fixture
def activity_registry():
    state = list(record.registry.items())
    yield record.registry
    record.registry.clear()
    for key, value in state:
        record.registry[key] = value


@pytest.fixture
def activity_muted(activity_registry, mocker):
    yield mocker.patch.object(record, "send")


@pytest.fixture(autouse=True)
def media_root(settings):
    """
    Sets settings.MEDIA_ROOT to a temporary path and returns this path
    """
    tmp_dir = tempfile.mkdtemp()
    settings.MEDIA_ROOT = tmp_dir
    yield settings.MEDIA_ROOT
    shutil.rmtree(tmp_dir)


@pytest.fixture
def r_mock():
    """
    Returns a requests_mock.mock() object you can use to mock HTTP calls made
    using python-requests
    """
    with requests_mock.mock() as m:
        yield m


@pytest.fixture
def authenticated_actor(factories, mocker):
    """
    Returns an authenticated ActivityPub actor
    """
    actor = factories["federation.Actor"]()
    mocker.patch(
        "funkwhale_api.federation.authentication.SignatureAuthentication.authenticate_actor",
        return_value=actor,
    )
    yield actor


@pytest.fixture
def assert_user_permission():
    def inner(view, permissions, operator="and"):
        assert HasUserPermission in view.permission_classes
        assert getattr(view, "permission_operator", "and") == operator
        assert set(view.required_permissions) == set(permissions)

    return inner


@pytest.fixture
def to_api_date():
    def inner(value):
        if isinstance(value, datetime.datetime):
            f = rest_fields.DateTimeField()
            return f.to_representation(value)
        if isinstance(value, datetime.date):
            f = rest_fields.DateField()
            return f.to_representation(value)
        raise ValueError("Invalid value: {}".format(value))

    return inner


@pytest.fixture()
def now(mocker):
    now = timezone.now()
    mocker.patch("django.utils.timezone.now", return_value=now)
    return now


@pytest.fixture()
def avatar():
    i = PIL.Image.new("RGBA", (400, 400), random.choice(["red", "blue", "yellow"]))
    f = io.BytesIO()
    i.save(f, "png")
    f.name = "avatar.png"
    f.seek(0)
    yield f
    f.close()
