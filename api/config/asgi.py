import os

import django

from .routing import application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

django.setup()
