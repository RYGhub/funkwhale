import os
from argparse import RawTextHelpFormatter

from django.core.management.base import BaseCommand

from django.db import transaction

from funkwhale_api.music import models


def progress(buffer, count, total, status=""):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    bar = "=" * filled_len + "-" * (bar_len - filled_len)

    buffer.write("[%s] %s/%s ...%s\r" % (bar, count, total, status))
    buffer.flush()


class Command(BaseCommand):
    help = """
    Loop through all in-place imported files in the database, and verify
    that the corresponding files are present on the filesystem. If some files are not
    found and --no-dry-run is specified, the corresponding database objects will be deleted.
    """

    def create_parser(self, *args, **kwargs):
        parser = super().create_parser(*args, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-dry-run",
            action="store_false",
            dest="dry_run",
            default=True,
            help="Disable dry run mode and apply pruning for real on the database",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        candidates = models.Upload.objects.filter(source__startswith="file://")
        candidates = candidates.filter(audio_file__in=["", None])
        total = candidates.count()
        self.stdout.write("Checking {} in-place imported files…".format(total))

        missing = []
        for i, row in enumerate(candidates.values("id", "source")):
            path = row["source"].replace("file://", "")
            progress(self.stdout, i + 1, total)
            if not os.path.exists(path):
                missing.append((path, row["id"]))

        if missing:
            for path, _ in missing:
                self.stdout.write("  {}".format(path))
            self.stdout.write(
                "The previous {} paths are referenced in database, but not found on disk!".format(
                    len(missing)
                )
            )

        else:
            self.stdout.write("All in-place imports have a matching on-disk file")
            return

        to_delete = candidates.filter(pk__in=[id for _, id in missing])
        if options["dry_run"]:
            self.stdout.write(
                "Nothing was deleted, rerun this command with --no-dry-run to apply the changes"
            )
        else:
            self.stdout.write("Deleting {} uploads…".format(to_delete.count()))
            to_delete.delete()
