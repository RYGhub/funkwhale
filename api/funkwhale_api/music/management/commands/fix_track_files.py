import cacheops
import os

from django.db import transaction
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from funkwhale_api.music import models, utils


class Command(BaseCommand):
    help = 'Run common checks and fix against imported tracks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Do not execute anything'
        )

    def handle(self, *args, **options):
        if options['dry_run']:
            self.stdout.write('Dry-run on, will not commit anything')
        self.fix_mimetypes(**options)
        cacheops.invalidate_model(models.TrackFile)

    @transaction.atomic
    def fix_mimetypes(self, dry_run, **kwargs):
        self.stdout.write('Fixing missing mimetypes...')
        matching = models.TrackFile.objects.filter(
            source__startswith='file://', mimetype=None)
        self.stdout.write(
            '[mimetypes] {} entries found with no mimetype'.format(
                matching.count()))
        for extension, mimetype in utils.EXTENSION_TO_MIMETYPE.items():
            qs = matching.filter(source__endswith='.{}'.format(extension))
            self.stdout.write(
                '[mimetypes] setting {} {} files to {}'.format(
                    qs.count(), extension, mimetype
                ))
            if not dry_run:
                self.stdout.write('[mimetypes] commiting...')
                qs.update(mimetype=mimetype)
