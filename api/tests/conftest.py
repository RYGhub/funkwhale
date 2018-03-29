import factory
import tempfile
import shutil
import pytest
import requests_mock

from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache as django_cache
from dynamic_preferences.registries import global_preferences_registry

from rest_framework.test import APIClient
from rest_framework.test import APIRequestFactory

from funkwhale_api.activity import record
from funkwhale_api.taskapp import celery


@pytest.fixture(scope="session", autouse=True)
def factories_autodiscover():
    from django.apps import apps
    from funkwhale_api import factories
    app_names = [app.name for app in apps.app_configs.values()]
    factories.registry.autodiscover(app_names)


@pytest.fixture(autouse=True)
def cache():
    yield django_cache
    django_cache.clear()


@pytest.fixture
def factories(db):
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
    from funkwhale_api import factories
    for v in factories.registry.values():
        try:
            v._meta.strategy = factory.BUILD_STRATEGY
        except AttributeError:
            # probably not a class based factory
            pass
    yield factories.registry


@pytest.fixture
def preferences(db):
    manager = global_preferences_registry.manager()
    manager.all()
    yield manager


@pytest.fixture
def tmpdir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)


@pytest.fixture
def logged_in_client(db, factories, client):
    user = factories['users.User']()
    assert client.login(username=user.username, password='test')
    setattr(client, 'user', user)
    yield client
    delattr(client, 'user')


@pytest.fixture
def anonymous_user():
    return AnonymousUser()


@pytest.fixture
def api_client(client):
    return APIClient()


@pytest.fixture
def logged_in_api_client(db, factories, api_client):
    user = factories['users.User']()
    assert api_client.login(username=user.username, password='test')
    setattr(api_client, 'user', user)
    yield api_client
    delattr(api_client, 'user')


@pytest.fixture
def superuser_api_client(db, factories, api_client):
    user = factories['users.SuperUser']()
    assert api_client.login(username=user.username, password='test')
    setattr(api_client, 'user', user)
    yield api_client
    delattr(api_client, 'user')


@pytest.fixture
def superuser_client(db, factories, client):
    user = factories['users.SuperUser']()
    assert client.login(username=user.username, password='test')
    setattr(client, 'user', user)
    yield client
    delattr(client, 'user')


@pytest.fixture
def api_request():
    return APIRequestFactory()


@pytest.fixture
def activity_registry():
    r = record.registry
    state = list(record.registry.items())
    yield record.registry
    record.registry.clear()
    for key, value in state:
        record.registry[key] = value


@pytest.fixture
def activity_registry():
    r = record.registry
    state = list(record.registry.items())
    yield record.registry
    record.registry.clear()
    for key, value in state:
        record.registry[key] = value


@pytest.fixture
def activity_muted(activity_registry, mocker):
    yield mocker.patch.object(record, 'send')


@pytest.fixture(autouse=True)
def media_root(settings):
    tmp_dir = tempfile.mkdtemp()
    settings.MEDIA_ROOT = tmp_dir
    yield settings.MEDIA_ROOT
    shutil.rmtree(tmp_dir)


@pytest.fixture
def r_mock():
    with requests_mock.mock() as m:
        yield m
