import glob
import os

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from funkwhale_api.music import models
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
            '--exit', '-x',
            action='store_true',
            dest='exit_on_failure',
            default=False,
            help='use this flag to disable error catching',
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

        filtered = self.filter_matching(matching, options)
        self.stdout.write('Import summary:')
        self.stdout.write('- {} files found matching this pattern: {}'.format(
            len(matching), options['path']))
        self.stdout.write('- {} files already found in database'.format(
            len(filtered['skipped'])))
        self.stdout.write('- {} new files'.format(
            len(filtered['new'])))

        if len(filtered['new']) == 0:
            self.stdout.write('Nothing new to import, exiting')
            return

        if options['interactive']:
            message = (
                'Are you sure you want to do this?\n\n'
                "Type 'yes' to continue, or 'no' to cancel: "
            )
            if input(''.join(message)) != 'yes':
                raise CommandError("Import cancelled.")

        batch, errors = self.do_import(
            filtered['new'], user=user, options=options)
        message = 'Successfully imported {} tracks'
        if options['async']:
            message = 'Successfully launched import for {} tracks'

        self.stdout.write(message.format(len(matching)))
        if len(errors) > 0:
            self.stderr.write(
                '{} tracks could not be imported:'.format(len(errors)))

            for path, error in errors:
                self.stderr('- {}: {}'.format(path, error))
        self.stdout.write(
            "For details, please refer to import batch #{}".format(batch.pk))

    def filter_matching(self, matching, options):
        sources = ['file://{}'.format(p) for p in matching]
        # we skip reimport for path that are already found
        # as a TrackFile.source
        existing = models.TrackFile.objects.filter(source__in=sources)
        existing = existing.values_list('source', flat=True)
        existing = set([p.replace('file://', '', 1) for p in existing])
        skipped = set(matching) & existing
        result = {
            'initial': matching,
            'skipped': list(skipped),
            'new': list(set(matching) - skipped)
        }
        return result

    def do_import(self, paths, user, options):
        message = '{i}/{total} Importing {path}...'
        if options['async']:
            message = '{i}/{total} Launching import for {path}...'

        # we create an import batch binded to the user
        async = options['async']
        import_handler = tasks.import_job_run.delay if async else tasks.import_job_run
        batch = user.imports.create(source='shell')
        total = len(paths)
        errors = []
        for i, path in enumerate(paths):
            try:
                self.stdout.write(
                    message.format(path=path, i=i+1, total=len(paths)))
                self.import_file(path, batch, import_handler, options)
            except Exception as e:
                if options['exit_on_failure']:
                    raise
                m = 'Error while importing {}: {} {}'.format(
                    path, e.__class__.__name__, e)
                self.stderr.write(m)
                errors.append((m, path))
        return batch, errors

    def import_file(self, path, batch, import_handler, options):
        job = batch.jobs.create(
            source='file://' + path,
        )
        name = os.path.basename(path)
        with open(path, 'rb') as f:
            job.audio_file.save(name, File(f))

        job.save()
        import_handler(
            import_job_id=job.pk,
            use_acoustid=not options['no_acoustid'])
