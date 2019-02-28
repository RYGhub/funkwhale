import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

import django  # noqa

django.setup()

from .routing import application  # noqa
