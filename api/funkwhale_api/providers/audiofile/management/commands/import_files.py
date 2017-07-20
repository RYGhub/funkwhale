import glob
from django.core.management.base import BaseCommand, CommandError
from funkwhale_api.providers.audiofile import importer


class Command(BaseCommand):
    help = 'Import audio files mathinc given glob pattern'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)
        parser.add_argument(
            '--recursive',
            action='store_true',
            dest='recursive',
            default=False,
            help='Will match the pattern recursively (including subdirectories)',
        )
        parser.add_argument(
            '--async',
            action='store_true',
            dest='async',
            default=False,
            help='Will launch celery tasks for each file to import instead of doing it synchronously and block the CLI',
        )
        parser.add_argument(
            '--noinput', '--no-input', action='store_false', dest='interactive',
            help="Do NOT prompt the user for input of any kind.",
        )

    def handle(self, *args, **options):
        # self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % poll_id))

        # Recursive is supported only on Python 3.5+, so we pass the option
        # only if it's True to avoid breaking on older versions of Python
        glob_kwargs = {}
        if options['recursive']:
            glob_kwargs['recursive'] = True
        try:
            matching = glob.glob(options['path'], **glob_kwargs)
        except TypeError:
            raise Exception('You need Python 3.5 to use the --recursive flag')

        self.stdout.write('This will import {} files matching this pattern: {}'.format(
            len(matching), options['path']))

        if not matching:
            raise CommandError('No file matching pattern, aborting')

        if options['interactive']:
            message = (
                'Are you sure you want to do this?\n\n'
                "Type 'yes' to continue, or 'no' to cancel: "
            )
            if input(''.join(message)) != 'yes':
                raise CommandError("Import cancelled.")

        message = 'Importing {}...'
        if options['async']:
            message = 'Launching import for {}...'

        for path in matching:
            self.stdout.write(message.format(path))
            try:
                importer.from_path(path)
            except Exception as e:
                self.stdout.write('Error: {}'.format(e))

        message = 'Successfully imported {} tracks'
        if options['async']:
            message = 'Successfully launched import for {} tracks'
        self.stdout.write(message.format(len(matching)))
