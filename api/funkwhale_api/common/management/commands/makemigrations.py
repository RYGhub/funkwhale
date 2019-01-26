import os

from django.core.management.base import CommandError
from django.core.management.commands.makemigrations import Command as BaseCommand


class Command(BaseCommand):
    def handle(self, *apps_label, **options):
        """
        Running makemigrations in production can have desastrous consequences.

        We ensure the command is disabled, unless a specific env var is provided.
        """
        force = os.environ.get("FORCE") == "1"
        if not force:
            raise CommandError(
                "Running makemigrations on your Funkwhale instance can have desastrous"
                " consequences. This command is disabled, and should only be run in "
                "development environments."
            )

        return super().handle(*apps_label, **options)
