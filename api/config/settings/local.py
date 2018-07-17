# -*- coding: utf-8 -*-
"""
Local settings

- Run in Debug mode
- Use console backend for emails
- Add Django Debug Toolbar
- Add django-extensions as app
"""

from .common import *  # noqa


# DEBUG
# ------------------------------------------------------------------------------
DEBUG = env.bool("DJANGO_DEBUG", default=True)
TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = env(
    "DJANGO_SECRET_KEY", default="mc$&b=5j#6^bv7tld1gyjp2&+^-qrdy=0sw@r5sua*1zp4fmxc"
)

# Mail settings
# ------------------------------------------------------------------------------
EMAIL_HOST = "localhost"
EMAIL_PORT = 1025

# django-debug-toolbar
# ------------------------------------------------------------------------------
MIDDLEWARE += ("debug_toolbar.middleware.DebugToolbarMiddleware",)

# INTERNAL_IPS = ('127.0.0.1', '10.0.2.2',)

DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
    "SHOW_TEMPLATE_CONTEXT": True,
    "SHOW_TOOLBAR_CALLBACK": lambda request: True,
    "JQUERY_URL": "",
}

# django-extensions
# ------------------------------------------------------------------------------
# INSTALLED_APPS += ('django_extensions', )
INSTALLED_APPS += ("debug_toolbar",)

# TESTING
# ------------------------------------------------------------------------------
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# CELERY
# In development, all tasks will be executed locally by blocking until the task returns
CELERY_TASK_ALWAYS_EAGER = False
# END CELERY

# Your local stuff: Below this line define 3rd party library settings

LOGGING = {
    "version": 1,
    "handlers": {"console": {"level": "DEBUG", "class": "logging.StreamHandler"}},
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "propagate": True,
            "level": "DEBUG",
        },
        "": {"level": "DEBUG", "handlers": ["console"]},
    },
}
CSRF_TRUSTED_ORIGINS = [o for o in ALLOWED_HOSTS]
