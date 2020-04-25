#!/usr/bin/env python
import django
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
    # we're doing this here since otherwise, missing environment
    # files in settings result in AttributeError being raised, generating
    # a cryptic django.core.exceptions.AppRegistryNotReady error.
    # To prevent that, we explicitely load settings here before anything
    # else, so we fail fast with a relevant error. See #140 for more details.
    django.setup()

    from django.core.management import execute_from_command_line

    if len(sys.argv) > 1 and sys.argv[1] in ["fw", "funkwhale"]:
        # trigger our own click-based cli
        from funkwhale_api.cli import main

        sys.argv = sys.argv[1:]
        main.invoke()
    else:
        execute_from_command_line(sys.argv)
