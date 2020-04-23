import itertools
import os
import urllib.parse
import time

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from funkwhale_api.music import models, tasks, utils


def crawl_dir(dir, extensions, recursive=True):
    if os.path.isfile(dir):
        yield dir
        return
    with os.scandir(dir) as scanner:
        for entry in scanner:
            if entry.is_file():
                for e in extensions:
                    if entry.name.lower().endswith(".{}".format(e.lower())):
                        yield entry.path
            elif recursive and entry.is_dir():
                yield from crawl_dir(entry, extensions, recursive=recursive)


def batch(iterable, n=1):
    has_entries = True
    while has_entries:
        current = []
        for i in range(0, n):
            try:
                current.append(next(iterable))
            except StopIteration:
                has_entries = False
        yield current


class Command(BaseCommand):
    help = "Import audio files mathinc given glob pattern"

    def add_arguments(self, parser):
        parser.add_argument(
            "library_id",
            type=str,
            help=(
                "A local library identifier where the files should be imported. "
                "You can use the full uuid such as e29c5be9-6da3-4d92-b40b-4970edd3ee4b "
                "or only a small portion of it, starting from the beginning, such as "
                "e29c5be9"
            ),
        )
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
            dest="async_",
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
            "--outbox",
            action="store_true",
            dest="outbox",
            default=False,
            help=(
                "Use this flag to notify library followers of newly imported files. "
                "You'll likely want to keep this disabled for CLI imports, especially if"
                "you plan to import hundreds or thousands of files, as it will cause a lot "
                "of overhead on your server and on servers you are federating with."
            ),
        )
        parser.add_argument("-e", "--extension", nargs="+")

        parser.add_argument(
            "--broadcast",
            action="store_true",
            dest="broadcast",
            default=False,
            help=(
                "Use this flag to enable realtime updates about the import in the UI. "
                "This causes some overhead, so it's disabled by default."
            ),
        )

        parser.add_argument(
            "--reference",
            action="store",
            dest="reference",
            default=None,
            help=(
                "A custom reference for the import. Leave this empty to have a random "
                "reference being generated for you."
            ),
        )
        parser.add_argument(
            "--noinput",
            "--no-input",
            action="store_false",
            dest="interactive",
            help="Do NOT prompt the user for input of any kind.",
        )

        parser.add_argument(
            "--batch-size",
            "-s",
            dest="batch_size",
            default=1000,
            type=int,
            help="Size of each batch, only used when crawling large collections",
        )

    def handle(self, *args, **options):
        self.is_confirmed = False
        try:
            library = models.Library.objects.select_related("actor__user").get(
                uuid__startswith=options["library_id"]
            )
        except models.Library.DoesNotExist:
            raise CommandError("Invalid library id")

        if not library.actor.get_user():
            raise CommandError("Library {} is not a local library".format(library.uuid))

        if options["in_place"]:
            self.stdout.write(
                "Checking imported paths against settings.MUSIC_DIRECTORY_PATH"
            )

            for import_path in options["path"]:
                p = settings.MUSIC_DIRECTORY_PATH
                if not p:
                    raise CommandError(
                        "Importing in-place requires setting the "
                        "MUSIC_DIRECTORY_PATH variable"
                    )
                if p and not import_path.startswith(p):
                    raise CommandError(
                        "Importing in-place only works if importing"
                        "from {} (MUSIC_DIRECTORY_PATH), as this directory"
                        "needs to be accessible by the webserver."
                        "Culprit: {}".format(p, import_path)
                    )

        extensions = options.get("extension") or utils.SUPPORTED_EXTENSIONS
        crawler = itertools.chain(
            *[
                crawl_dir(p, extensions=extensions, recursive=options["recursive"])
                for p in options["path"]
            ]
        )
        errors = []
        total = 0
        start_time = time.time()
        reference = options["reference"] or "cli-{}".format(timezone.now().isoformat())

        import_url = "{}://{}/library/{}/upload?{}"
        import_url = import_url.format(
            settings.FUNKWHALE_PROTOCOL,
            settings.FUNKWHALE_HOSTNAME,
            str(library.uuid),
            urllib.parse.urlencode([("import", reference)]),
        )
        self.stdout.write(
            "For details, please refer to import reference '{}' or URL {}".format(
                reference, import_url
            )
        )
        batch_start = None
        batch_duration = None
        for i, entries in enumerate(batch(crawler, options["batch_size"])):
            total += len(entries)
            batch_start = time.time()
            time_stats = ""
            if i > 0:
                time_stats = " - running for {}s, previous batch took {}s".format(
                    int(time.time() - start_time), int(batch_duration),
                )
            if entries:
                self.stdout.write(
                    "Handling batch {} ({} items){}".format(
                        i + 1, options["batch_size"], time_stats,
                    )
                )
                batch_errors = self.handle_batch(
                    library=library,
                    paths=entries,
                    batch=i + 1,
                    reference=reference,
                    options=options,
                )
                if batch_errors:
                    errors += batch_errors

            batch_duration = time.time() - batch_start

        message = "Successfully imported {} tracks in {}s"
        if options["async_"]:
            message = "Successfully launched import for {} tracks in {}s"

        self.stdout.write(
            message.format(total - len(errors), int(time.time() - start_time))
        )
        if len(errors) > 0:
            self.stderr.write("{} tracks could not be imported:".format(len(errors)))

            for path, error in errors:
                self.stderr.write("- {}: {}".format(path, error))

        self.stdout.write(
            "For details, please refer to import reference '{}' or URL {}".format(
                reference, import_url
            )
        )

    def handle_batch(self, library, paths, batch, reference, options):
        matching = []
        for m in paths:
            # In some situations, the path is encoded incorrectly on the filesystem
            # so we filter out faulty paths and display a warning to the user.
            # see https://dev.funkwhale.audio/funkwhale/funkwhale/issues/138
            try:
                m.encode("utf-8")
                matching.append(m)
            except UnicodeEncodeError:
                try:
                    previous = matching[-1]
                except IndexError:
                    previous = None
                self.stderr.write(
                    self.style.WARNING(
                        "[warning] Ignoring undecodable path. Previous ok file was {}".format(
                            previous
                        )
                    )
                )

        if not matching:
            raise CommandError("No file matching pattern, aborting")

        if options["replace"]:
            filtered = {"initial": matching, "skipped": [], "new": matching}
            message = "  - {} files to be replaced"
            import_paths = matching
        else:
            filtered = self.filter_matching(matching, library)
            message = "  - {} files already found in database"
            import_paths = filtered["new"]

        self.stdout.write("  Import summary:")
        self.stdout.write(
            "  - {} files found matching this pattern: {}".format(
                len(matching), options["path"]
            )
        )
        self.stdout.write(message.format(len(filtered["skipped"])))

        self.stdout.write("  - {} new files".format(len(filtered["new"])))

        if batch == 1:
            self.stdout.write(
                "  Selected options: {}".format(
                    ", ".join(
                        ["in place" if options["in_place"] else "copy music files"]
                    )
                )
            )
        if len(filtered["new"]) == 0:
            self.stdout.write("  Nothing new to import, exiting")
            return

        if options["interactive"] and not self.is_confirmed:
            message = (
                "Are you sure you want to do this?\n\n"
                "Type 'yes' to continue, or 'no' to cancel: "
            )
            if input("".join(message)) != "yes":
                raise CommandError("Import cancelled.")
            self.is_confirmed = True

        errors = self.do_import(
            import_paths,
            library=library,
            reference=reference,
            batch=batch,
            options=options,
        )
        return errors

    def filter_matching(self, matching, library):
        sources = ["file://{}".format(p) for p in matching]
        # we skip reimport for path that are already found
        # as a Upload.source
        existing = library.uploads.filter(source__in=sources, import_status="finished")
        existing = existing.values_list("source", flat=True)
        existing = set([p.replace("file://", "", 1) for p in existing])
        skipped = set(matching) & existing
        result = {
            "initial": matching,
            "skipped": list(sorted(skipped)),
            "new": list(sorted(set(matching) - skipped)),
        }
        return result

    def do_import(self, paths, library, reference, batch, options):
        message = "[batch {batch}] {i}/{total} Importing {path}..."
        if options["async_"]:
            message = "[batch {batch}] {i}/{total} Launching import for {path}..."

        # we create an upload binded to the library
        async_ = options["async_"]
        errors = []
        for i, path in list(enumerate(paths)):
            if options["verbosity"] > 1:
                self.stdout.write(
                    message.format(batch=batch, path=path, i=i + 1, total=len(paths))
                )
            try:
                self.create_upload(
                    path,
                    reference,
                    library,
                    async_,
                    options["replace"],
                    options["in_place"],
                    options["outbox"],
                    options["broadcast"],
                )
            except Exception as e:
                if options["exit_on_failure"]:
                    raise
                m = "Error while importing {}: {} {}".format(
                    path, e.__class__.__name__, e
                )
                self.stderr.write(m)
                errors.append((path, "{} {}".format(e.__class__.__name__, e)))
        return errors

    def create_upload(
        self,
        path,
        reference,
        library,
        async_,
        replace,
        in_place,
        dispatch_outbox,
        broadcast,
    ):
        import_handler = tasks.process_upload.delay if async_ else tasks.process_upload
        upload = models.Upload(library=library, import_reference=reference)
        upload.source = "file://" + path
        upload.import_metadata = {
            "funkwhale": {
                "config": {
                    "replace": replace,
                    "dispatch_outbox": dispatch_outbox,
                    "broadcast": broadcast,
                }
            }
        }
        if not in_place:
            name = os.path.basename(path)
            with open(path, "rb") as f:
                upload.audio_file.save(name, File(f), save=False)

        upload.save()

        import_handler(upload_id=upload.pk)
