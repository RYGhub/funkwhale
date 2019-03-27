from argparse import RawTextHelpFormatter

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from django.db import transaction

from funkwhale_api.music import models, tasks


class Command(BaseCommand):
    help = """
    Remove tracks, albums and artists that are not associated with any file from the instance library:

    - Tracks without uploads are deleted, if the --tracks flag is passed
    - Albums without tracks are deleted, if the --albums flag is passed
    - Artists without albums are deleted, if the --artists flag is passed

    Tracks with associated favorites, playlists or listening won't be deleted
    by default, unless you pass the corresponding --ignore-* flags.

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
        parser.add_argument(
            "--artists",
            action="store_true",
            dest="prune_artists",
            default=False,
            help="Prune artists without albums/tracks",
        )
        parser.add_argument(
            "--albums",
            action="store_true",
            dest="prune_albums",
            default=False,
            help="Prune albums without tracks",
        )
        parser.add_argument(
            "--tracks",
            action="store_true",
            dest="prune_tracks",
            default=False,
            help="Prune tracks without uploads",
        )

        parser.add_argument(
            "--ignore-favorites",
            action="store_false",
            dest="exclude_favorites",
            default=True,
            help="Allow favorited tracks to be pruned",
        )

        parser.add_argument(
            "--ignore-playlists",
            action="store_false",
            dest="exclude_playlists",
            default=True,
            help="Allow tracks included in playlists to be pruned",
        )

        parser.add_argument(
            "--ignore-listenings",
            action="store_false",
            dest="exclude_listenings",
            default=True,
            help="Allow tracks with listening history to be pruned",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if not any(
            [options["prune_albums"], options["prune_tracks"], options["prune_artists"]]
        ):
            raise CommandError(
                "You need to provide at least one of the --tracks, --albums or --artists flags"
            )

        if options["dry_run"]:
            self.stdout.write("Dry-run on, will not commit anything")
        else:
            self.stdout.write("Dry-run off, *pruning for real*")
        self.stdout.write("")
        if options["prune_tracks"]:
            prunable = tasks.get_prunable_tracks(
                exclude_favorites=options["exclude_favorites"],
                exclude_playlists=options["exclude_playlists"],
                exclude_listenings=options["exclude_listenings"],
            )
            pruned_total = prunable.count()
            total = models.Track.objects.count()
            if options["dry_run"]:
                self.stdout.write(
                    "Would prune {}/{} tracks".format(pruned_total, total)
                )
            else:
                self.stdout.write("Deleting {}/{} tracks…".format(pruned_total, total))
                prunable.delete()

        if options["prune_albums"]:
            prunable = tasks.get_prunable_albums()
            pruned_total = prunable.count()
            total = models.Album.objects.count()
            if options["dry_run"]:
                self.stdout.write(
                    "Would prune {}/{} albums".format(pruned_total, total)
                )
            else:
                self.stdout.write("Deleting {}/{} albums…".format(pruned_total, total))
                prunable.delete()

        if options["prune_artists"]:
            prunable = tasks.get_prunable_artists()
            pruned_total = prunable.count()
            total = models.Artist.objects.count()
            if options["dry_run"]:
                self.stdout.write(
                    "Would prune {}/{} artists".format(pruned_total, total)
                )
            else:
                self.stdout.write("Deleting {}/{} artists…".format(pruned_total, total))
                prunable.delete()

        self.stdout.write("")
        if options["dry_run"]:
            self.stdout.write(
                "Nothing was pruned, rerun this command with --no-dry-run to apply the changes"
            )
        else:
            self.stdout.write("Pruning completed!")

        self.stdout.write("")
