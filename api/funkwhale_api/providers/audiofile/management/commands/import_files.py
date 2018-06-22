import glob
import os

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from funkwhale_api.music import models, tasks
from funkwhale_api.users.models import User


class Command(BaseCommand):
    help = "Import audio files mathinc given glob pattern"

    def add_arguments(self, parser):
        parser.add_argument("path", nargs="+", type=str)
        parser.add_argument(
            "--recursive",
            action="store_true",
            dest="recursive",
            default=False,
            help="Will match the pattern recursively (including subdirectories)",
        )
        parser.add_argument(
            "--username",
            dest="username",
            help="The username of the user you want to be bound to the import",
        )
        parser.add_argument(
            "--async",
            action="store_true",
            dest="async",
            default=False,
            help="Will launch celery tasks for each file to import instead of doing it synchronously and block the CLI",
        )
        parser.add_argument(
            "--exit",
            "-x",
            action="store_true",
            dest="exit_on_failure",
            default=False,
            help="Use this flag to disable error catching",
        )
        parser.add_argument(
            "--in-place",
            "-i",
            action="store_true",
            dest="in_place",
            default=False,
            help=(
                "Import files without duplicating them into the media directory."
                "For in-place import to work, the music files must be readable"
                "by the web-server and funkwhale api and celeryworker processes."
                "You may want to use this if you have a big music library to "
                "import and not much disk space available."
            ),
        )
        parser.add_argument(
            "--replace",
            action="store_true",
            dest="replace",
            default=False,
            help=(
                "Use this flag to replace duplicates (tracks with same "
                "musicbrainz mbid, or same artist, album and title) on import "
                "with their newest version."
            ),
        )
        parser.add_argument(
            "--noinput",
            "--no-input",
            action="store_false",
            dest="interactive",
            help="Do NOT prompt the user for input of any kind.",
        )

    def handle(self, *args, **options):
        glob_kwargs = {}
        matching = []
        if options["recursive"]:
            glob_kwargs["recursive"] = True
        try:
            for import_path in options["path"]:
                matching += glob.glob(import_path, **glob_kwargs)
            matching = sorted(list(set(matching)))
        except TypeError:
            raise Exception("You need Python 3.5 to use the --recursive flag")

        if options["in_place"]:
            self.stdout.write(
                "Checking imported paths against settings.MUSIC_DIRECTORY_PATH"
            )
            p = settings.MUSIC_DIRECTORY_PATH
            if not p:
                raise CommandError(
                    "Importing in-place requires setting the "
                    "MUSIC_DIRECTORY_PATH variable"
                )
            for m in matching:
                if not m.startswith(p):
                    raise CommandError(
                        "Importing in-place only works if importing"
                        "from {} (MUSIC_DIRECTORY_PATH), as this directory"
                        "needs to be accessible by the webserver."
                        "Culprit: {}".format(p, m)
                    )
        if not matching:
            raise CommandError("No file matching pattern, aborting")

        user = None
        if options["username"]:
            try:
                user = User.objects.get(username=options["username"])
            except User.DoesNotExist:
                raise CommandError("Invalid username")
        else:
            # we bind the import to the first registered superuser
            try:
                user = User.objects.filter(is_superuser=True).order_by("pk").first()
                assert user is not None
            except AssertionError:
                raise CommandError(
                    "No superuser available, please provide a --username"
                )

        if options["replace"]:
            filtered = {"initial": matching, "skipped": [], "new": matching}
            message = "- {} files to be replaced"
            import_paths = matching
        else:
            filtered = self.filter_matching(matching)
            message = "- {} files already found in database"
            import_paths = filtered["new"]

        self.stdout.write("Import summary:")
        self.stdout.write(
            "- {} files found matching this pattern: {}".format(
                len(matching), options["path"]
            )
        )
        self.stdout.write(message.format(len(filtered["skipped"])))

        self.stdout.write("- {} new files".format(len(filtered["new"])))

        self.stdout.write(
            "Selected options: {}".format(
                ", ".join(["in place" if options["in_place"] else "copy music files"])
            )
        )
        if len(filtered["new"]) == 0:
            self.stdout.write("Nothing new to import, exiting")
            return

        if options["interactive"]:
            message = (
                "Are you sure you want to do this?\n\n"
                "Type 'yes' to continue, or 'no' to cancel: "
            )
            if input("".join(message)) != "yes":
                raise CommandError("Import cancelled.")

        batch, errors = self.do_import(import_paths, user=user, options=options)
        message = "Successfully imported {} tracks"
        if options["async"]:
            message = "Successfully launched import for {} tracks"

        self.stdout.write(message.format(len(import_paths)))
        if len(errors) > 0:
            self.stderr.write("{} tracks could not be imported:".format(len(errors)))

            for path, error in errors:
                self.stderr.write("- {}: {}".format(path, error))
        self.stdout.write(
            "For details, please refer to import batch #{}".format(batch.pk)
        )

    def filter_matching(self, matching):
        sources = ["file://{}".format(p) for p in matching]
        # we skip reimport for path that are already found
        # as a TrackFile.source
        existing = models.TrackFile.objects.filter(source__in=sources)
        existing = existing.values_list("source", flat=True)
        existing = set([p.replace("file://", "", 1) for p in existing])
        skipped = set(matching) & existing
        result = {
            "initial": matching,
            "skipped": list(sorted(skipped)),
            "new": list(sorted(set(matching) - skipped)),
        }
        return result

    def do_import(self, paths, user, options):
        message = "{i}/{total} Importing {path}..."
        if options["async"]:
            message = "{i}/{total} Launching import for {path}..."

        # we create an import batch binded to the user
        async = options["async"]
        import_handler = tasks.import_job_run.delay if async else tasks.import_job_run
        batch = user.imports.create(source="shell")
        errors = []
        for i, path in list(enumerate(paths)):
            try:
                self.stdout.write(message.format(path=path, i=i + 1, total=len(paths)))
                self.import_file(path, batch, import_handler, options)
            except Exception as e:
                if options["exit_on_failure"]:
                    raise
                m = "Error while importing {}: {} {}".format(
                    path, e.__class__.__name__, e
                )
                self.stderr.write(m)
                errors.append((path, "{} {}".format(e.__class__.__name__, e)))
        return batch, errors

    def import_file(self, path, batch, import_handler, options):
        job = batch.jobs.create(source="file://" + path)
        if not options["in_place"]:
            name = os.path.basename(path)
            with open(path, "rb") as f:
                job.audio_file.save(name, File(f))

            job.save()
        import_handler(import_job_id=job.pk, use_acoustid=False)
