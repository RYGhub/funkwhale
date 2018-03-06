import glob
import os

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from funkwhale_api.common import utils
from funkwhale_api.music import tasks
from funkwhale_api.users.models import User


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
            '--username',
            dest='username',
            help='The username of the user you want to be bound to the import',
        )
        parser.add_argument(
            '--async',
            action='store_true',
            dest='async',
            default=False,
            help='Will launch celery tasks for each file to import instead of doing it synchronously and block the CLI',
        )
        parser.add_argument(
            '--no-acoustid',
            action='store_true',
            dest='no_acoustid',
            default=False,
            help='Use this flag to completely bypass acoustid completely',
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

        user = None
        if options['username']:
            try:
                user = User.objects.get(username=options['username'])
            except User.DoesNotExist:
                raise CommandError('Invalid username')
        else:
            # we bind the import to the first registered superuser
            try:
                user = User.objects.filter(is_superuser=True).order_by('pk').first()
                assert user is not None
            except AssertionError:
                raise CommandError(
                    'No superuser available, please provide a --username')
        if options['interactive']:
            message = (
                'Are you sure you want to do this?\n\n'
                "Type 'yes' to continue, or 'no' to cancel: "
            )
            if input(''.join(message)) != 'yes':
                raise CommandError("Import cancelled.")

        batch = self.do_import(matching, user=user, options=options)

        message = 'Successfully imported {} tracks'
        if options['async']:
            message = 'Successfully launched import for {} tracks'
        self.stdout.write(message.format(len(matching)))
        self.stdout.write(
            "For details, please refer to import batch #".format(batch.pk))

    @transaction.atomic
    def do_import(self, matching, user, options):
        message = 'Importing {}...'
        if options['async']:
            message = 'Launching import for {}...'

        # we create an import batch binded to the user
        batch = user.imports.create(source='shell')
        async = options['async']
        import_handler = tasks.import_job_run.delay if async else tasks.import_job_run
        for path in matching:
            job = batch.jobs.create(
                source='file://' + path,
            )
            name = os.path.basename(path)
            with open(path, 'rb') as f:
                job.audio_file.save(name, File(f))

            job.save()
            try:
                utils.on_commit(
                    import_handler,
                    import_job_id=job.pk,
                    use_acoustid=not options['no_acoustid'])
            except Exception as e:
                self.stdout.write('Error: {}'.format(e))

        return batch
