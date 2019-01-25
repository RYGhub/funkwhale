from __future__ import absolute_import

import functools
import traceback as tb
import os
import logging
import celery.app.task
from django.apps import AppConfig
from django.conf import settings


logger = logging.getLogger("celery")

if not settings.configured:
    # set the default Django settings module for the 'celery' program.
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "config.settings.production"
    )  # pragma: no cover

app = celery.Celery("funkwhale_api")


@celery.signals.task_failure.connect
def process_failure(sender, task_id, exception, args, kwargs, traceback, einfo, **kw):
    print("[celery] Error during task {}: {}".format(task_id, einfo.exception))
    tb.print_exc()


class CeleryConfig(AppConfig):
    name = "funkwhale_api.taskapp"
    verbose_name = "Celery Config"

    def ready(self):
        # Using a string here means the worker will not have to
        # pickle the object when using Windows.
        app.config_from_object("django.conf:settings", namespace="CELERY")
        app.autodiscover_tasks(lambda: settings.INSTALLED_APPS, force=True)


def require_instance(model_or_qs, parameter_name, id_kwarg_name=None):
    def decorator(function):
        @functools.wraps(function)
        def inner(*args, **kwargs):
            kw = id_kwarg_name or "_".join([parameter_name, "id"])
            pk = kwargs.pop(kw)
            try:
                instance = model_or_qs.get(pk=pk)
            except AttributeError:
                instance = model_or_qs.objects.get(pk=pk)
            kwargs[parameter_name] = instance
            return function(*args, **kwargs)

        return inner

    return decorator
