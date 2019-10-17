import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
os.environ.setdefault("ASGI_THREADS", "5")

import django  # noqa

django.setup()

from .routing import application  # noqa
