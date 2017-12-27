
from __future__ import absolute_import
import os
import functools

from celery import Celery
from django.apps import AppConfig
from django.conf import settings


if not settings.configured:
    # set the default Django settings module for the 'celery' program.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")  # pragma: no cover


app = Celery('funkwhale_api')


class CeleryConfig(AppConfig):
    name = 'funkwhale_api.taskapp'
    verbose_name = 'Celery Config'

    def ready(self):
        # Using a string here means the worker will not have to
        # pickle the object when using Windows.
        app.config_from_object('django.conf:settings', namespace='CELERY')
        app.autodiscover_tasks(lambda: settings.INSTALLED_APPS, force=True)


def require_instance(model_or_qs, parameter_name):
    def decorator(function):
        @functools.wraps(function)
        def inner(*args, **kwargs):
            pk = kwargs.pop('_'.join([parameter_name, 'id']))
            try:
                instance = model_or_qs.get(pk=pk)
            except AttributeError:
                instance = model_or_qs.objects.get(pk=pk)
            kwargs[parameter_name] = instance
            return function(*args, **kwargs)
        return inner
    return decorator
