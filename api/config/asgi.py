import os

import django

django.setup()

from .routing import application  # noqa

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
