from django.apps import AppConfig, apps

from . import mrf


class ModerationConfig(AppConfig):
    name = "funkwhale_api.moderation"

    def ready(self):
        super().ready()

        app_names = [app.name for app in apps.app_configs.values()]
        mrf.inbox.autodiscover(app_names)
