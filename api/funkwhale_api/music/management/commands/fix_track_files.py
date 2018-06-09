import cacheops

from django.db import transaction
from django.db.models import Q
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from funkwhale_api.music import models, utils


class Command(BaseCommand):
    help = "Run common checks and fix against imported tracks"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            default=False,
            help="Do not execute anything",
        )

    def handle(self, *args, **options):
        if options["dry_run"]:
            self.stdout.write("Dry-run on, will not commit anything")
        self.fix_mimetypes(**options)
        self.fix_file_data(**options)
        self.fix_file_size(**options)
        cacheops.invalidate_model(models.TrackFile)

    @transaction.atomic
    def fix_mimetypes(self, dry_run, **kwargs):
        self.stdout.write("Fixing missing mimetypes...")
        matching = models.TrackFile.objects.filter(
            source__startswith="file://"
        ).exclude(mimetype__startswith="audio/")
        self.stdout.write(
            "[mimetypes] {} entries found with bad or no mimetype".format(
                matching.count()
            )
        )
        for extension, mimetype in utils.EXTENSION_TO_MIMETYPE.items():
            qs = matching.filter(source__endswith=".{}".format(extension))
            self.stdout.write(
                "[mimetypes] setting {} {} files to {}".format(
                    qs.count(), extension, mimetype
                )
            )
            if not dry_run:
                self.stdout.write("[mimetypes] commiting...")
                qs.update(mimetype=mimetype)

    def fix_file_data(self, dry_run, **kwargs):
        self.stdout.write("Fixing missing bitrate or length...")
        matching = models.TrackFile.objects.filter(
            Q(bitrate__isnull=True) | Q(duration__isnull=True)
        )
        total = matching.count()
        self.stdout.write(
            "[bitrate/length] {} entries found with missing values".format(total)
        )
        if dry_run:
            return
        for i, tf in enumerate(matching.only("audio_file")):
            self.stdout.write(
                "[bitrate/length] {}/{} fixing file #{}".format(i + 1, total, tf.pk)
            )

            try:
                audio_file = tf.get_audio_file()
                if audio_file:
                    with audio_file as f:
                        data = utils.get_audio_file_data(audio_file)
                    tf.bitrate = data["bitrate"]
                    tf.duration = data["length"]
                    tf.save(update_fields=["duration", "bitrate"])
                else:
                    self.stderr.write("[bitrate/length] no file found")
            except Exception as e:
                self.stderr.write(
                    "[bitrate/length] error with file #{}: {}".format(tf.pk, str(e))
                )

    def fix_file_size(self, dry_run, **kwargs):
        self.stdout.write("Fixing missing size...")
        matching = models.TrackFile.objects.filter(size__isnull=True)
        total = matching.count()
        self.stdout.write("[size] {} entries found with missing values".format(total))
        if dry_run:
            return
        for i, tf in enumerate(matching.only("size")):
            self.stdout.write(
                "[size] {}/{} fixing file #{}".format(i + 1, total, tf.pk)
            )

            try:
                tf.size = tf.get_file_size()
                tf.save(update_fields=["size"])
            except Exception as e:
                self.stderr.write(
                    "[size] error with file #{}: {}".format(tf.pk, str(e))
                )
