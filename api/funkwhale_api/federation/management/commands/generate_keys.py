from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from dynamic_preferences.registries import global_preferences_registry

from funkwhale_api.federation import keys


class Command(BaseCommand):
    help = (
        'Generate a public/private key pair for your instance,'
        ' for federation purposes. If a key pair already exists, does nothing.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--replace',
            action='store_true',
            dest='replace',
            default=False,
            help='Replace existing key pair, if any',
        )
        parser.add_argument(
            '--noinput', '--no-input', action='store_false', dest='interactive',
            help="Do NOT prompt the user for input of any kind.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        preferences = global_preferences_registry.manager()
        existing_public = preferences['federation__public_key']
        existing_private = preferences['federation__public_key']

        if existing_public or existing_private and not options['replace']:
            raise CommandError(
                'Keys are already present! '
                'Replace them with --replace if you know what you are doing.')

        if options['interactive']:
            message = (
                'Are you sure you want to do this?\n\n'
                "Type 'yes' to continue, or 'no' to cancel: "
            )
            if input(''.join(message)) != 'yes':
                raise CommandError("Operation cancelled.")
        private, public = keys.get_key_pair()
        preferences['federation__public_key'] = public.decode('utf-8')
        preferences['federation__private_key'] = private.decode('utf-8')

        self.stdout.write(
            'Your new key pair was generated.'
            'Your public key is now:\n\n{}'.format(public.decode('utf-8'))
        )
