import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

django.setup()

from .routing import application
