import tempfile
import shutil
import pytest
from django.core.cache import cache as django_cache
from dynamic_preferences.registries import global_preferences_registry
from rest_framework.test import APIClient

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
def superuser_client(db, factories, client):
    user = factories['users.SuperUser']()
    assert client.login(username=user.username, password='test')
    setattr(client, 'user', user)
    yield client
    delattr(client, 'user')
