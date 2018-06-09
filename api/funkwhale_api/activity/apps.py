from django.apps import AppConfig, apps

from . import record


class ActivityConfig(AppConfig):
    name = "funkwhale_api.activity"

    def ready(self):
        super(ActivityConfig, self).ready()

        app_names = [app.name for app in apps.app_configs.values()]
        record.registry.autodiscover(app_names)
