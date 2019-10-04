import math
import random

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction


from funkwhale_api.federation import keys
from funkwhale_api.federation import models as federation_models
from funkwhale_api.music import models as music_models
from funkwhale_api.tags import models as tags_models
from funkwhale_api.users import models as users_models


BATCH_SIZE = 500


def create_local_accounts(factories, count, dependencies):
    password = factories["users.User"].build().password
    users = factories["users.User"].build_batch(size=count)
    for user in users:
        # we set the hashed password by hand, because computing one for each user
        # is CPU intensive
        user.password = password
    users = users_models.User.objects.bulk_create(users, batch_size=BATCH_SIZE)
    actors = []
    domain = federation_models.Domain.objects.get_or_create(
        name=settings.FEDERATION_HOSTNAME
    )[0]
    users = [u for u in users if u.pk]
    private, public = keys.get_key_pair()
    for user in users:
        if not user.pk:
            continue
        actor = federation_models.Actor(
            private_key=private.decode("utf-8"),
            public_key=public.decode("utf-8"),
            **users_models.get_actor_data(user.username, domain=domain)
        )
        actors.append(actor)
    actors = federation_models.Actor.objects.bulk_create(actors, batch_size=BATCH_SIZE)
    for user, actor in zip(users, actors):
        user.actor = actor
    users_models.User.objects.bulk_update(users, ["actor"])
    return actors


def create_taggable_items(dependency):
    def inner(factories, count, dependencies):

        objs = []
        tagged_objects = dependencies.get(
            dependency, list(CONFIG_BY_ID[dependency]["model"].objects.all().only("pk"))
        )
        tags = dependencies.get("tags", list(tags_models.Tag.objects.all().only("pk")))
        for i in range(count):
            tag = random.choice(tags)
            tagged_object = random.choice(tagged_objects)
            objs.append(
                factories["tags.TaggedItem"].build(
                    content_object=tagged_object, tag=tag
                )
            )

        return tags_models.TaggedItem.objects.bulk_create(
            objs, batch_size=BATCH_SIZE, ignore_conflicts=True
        )

    return inner


CONFIG = [
    {
        "id": "tracks",
        "model": music_models.Track,
        "factory": "music.Track",
        "factory_kwargs": {"artist": None, "album": None},
        "depends_on": [
            {"field": "album", "id": "albums", "default_factor": 0.1},
            {"field": "artist", "id": "artists", "default_factor": 0.05},
        ],
    },
    {
        "id": "albums",
        "model": music_models.Album,
        "factory": "music.Album",
        "factory_kwargs": {"artist": None},
        "depends_on": [{"field": "artist", "id": "artists", "default_factor": 0.3}],
    },
    {"id": "artists", "model": music_models.Artist, "factory": "music.Artist"},
    {
        "id": "local_accounts",
        "model": federation_models.Actor,
        "handler": create_local_accounts,
    },
    {
        "id": "local_libraries",
        "model": music_models.Library,
        "factory": "music.Library",
        "factory_kwargs": {"actor": None},
        "depends_on": [{"field": "actor", "id": "local_accounts", "default_factor": 1}],
    },
    {
        "id": "local_uploads",
        "model": music_models.Upload,
        "factory": "music.Upload",
        "factory_kwargs": {"import_status": "finished", "library": None, "track": None},
        "depends_on": [
            {
                "field": "library",
                "id": "local_libraries",
                "default_factor": 0.05,
                "queryset": music_models.Library.objects.all().select_related(
                    "actor__user"
                ),
            },
            {"field": "track", "id": "tracks", "default_factor": 1},
        ],
    },
    {"id": "tags", "model": tags_models.Tag, "factory": "tags.Tag"},
    {
        "id": "track_tags",
        "model": tags_models.TaggedItem,
        "queryset": tags_models.TaggedItem.objects.filter(
            content_type__app_label="music", content_type__model="track"
        ),
        "handler": create_taggable_items("tracks"),
        "depends_on": [
            {
                "field": "tag",
                "id": "tags",
                "default_factor": 0.1,
                "queryset": tags_models.Tag.objects.all(),
                "set": False,
            },
            {
                "field": "content_object",
                "id": "tracks",
                "default_factor": 1,
                "set": False,
            },
        ],
    },
    {
        "id": "album_tags",
        "model": tags_models.TaggedItem,
        "queryset": tags_models.TaggedItem.objects.filter(
            content_type__app_label="music", content_type__model="album"
        ),
        "handler": create_taggable_items("albums"),
        "depends_on": [
            {
                "field": "tag",
                "id": "tags",
                "default_factor": 0.1,
                "queryset": tags_models.Tag.objects.all(),
                "set": False,
            },
            {
                "field": "content_object",
                "id": "albums",
                "default_factor": 1,
                "set": False,
            },
        ],
    },
    {
        "id": "artist_tags",
        "model": tags_models.TaggedItem,
        "queryset": tags_models.TaggedItem.objects.filter(
            content_type__app_label="music", content_type__model="artist"
        ),
        "handler": create_taggable_items("artists"),
        "depends_on": [
            {
                "field": "tag",
                "id": "tags",
                "default_factor": 0.1,
                "queryset": tags_models.Tag.objects.all(),
                "set": False,
            },
            {
                "field": "content_object",
                "id": "artists",
                "default_factor": 1,
                "set": False,
            },
        ],
    },
]

CONFIG_BY_ID = {c["id"]: c for c in CONFIG}


class Rollback(Exception):
    pass


def create_objects(row, factories, count, **factory_kwargs):
    return factories[row["factory"]].build_batch(size=count, **factory_kwargs)


class Command(BaseCommand):
    help = """
    Inject demo data into your database. Useful for load testing, or setting up a demo instance.

    Use with caution and only if you know what you are doing.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-dry-run",
            action="store_false",
            dest="dry_run",
            help="Commit the changes to the database",
        )
        parser.add_argument(
            "--create-dependencies", action="store_true", dest="create_dependencies"
        )
        for row in CONFIG:
            parser.add_argument(
                "--{}".format(row["id"].replace("_", "-")),
                dest=row["id"],
                type=int,
                help="Number of {} objects to create".format(row["id"]),
            )
            dependencies = row.get("depends_on", [])
            for dependency in dependencies:
                parser.add_argument(
                    "--{}-{}-factor".format(row["id"], dependency["field"]),
                    dest="{}_{}_factor".format(row["id"], dependency["field"]),
                    type=float,
                    help="Number of {} objects to create per {} object".format(
                        dependency["id"], row["id"]
                    ),
                )

    def handle(self, *args, **options):
        from django.apps import apps
        from funkwhale_api import factories

        app_names = [app.name for app in apps.app_configs.values()]
        factories.registry.autodiscover(app_names)
        try:
            return self.inner_handle(*args, **options)
        except Rollback:
            pass

    @transaction.atomic
    def inner_handle(self, *args, **options):
        results = {}
        for row in CONFIG:
            self.create_batch(row, results, options, count=options.get(row["id"]))

        self.stdout.write("\nFinal state of database:\n\n")
        for row in CONFIG:
            qs = row.get("queryset", row["model"].objects.all())
            total = qs.count()
            self.stdout.write("- {} {} objects".format(total, row["id"]))

        self.stdout.write("")
        if options["dry_run"]:

            self.stdout.write(
                "Run this command with --no-dry-run to commit the changes to the database"
            )
            raise Rollback()

        self.stdout.write(self.style.SUCCESS("Done!"))

    def create_batch(self, row, results, options, count):
        from funkwhale_api import factories

        if row["id"] in results:
            # already generated
            return results[row["id"]]
        if not count:
            return []
        dependencies = row.get("depends_on", [])
        create_dependencies = options.get("create_dependencies")
        for dependency in dependencies:
            dep_count = options.get(dependency["id"])
            if not create_dependencies and dep_count is None:
                continue
            if dep_count is None:
                factor = options[
                    "{}_{}_factor".format(row["id"], dependency["field"])
                ] or dependency.get("default_factor")
                dep_count = math.ceil(factor * count)

            results[dependency["id"]] = self.create_batch(
                CONFIG_BY_ID[dependency["id"]], results, options, count=dep_count
            )
        self.stdout.write("Creating {} {}…".format(count, row["id"]))
        handler = row.get("handler")
        if handler:
            objects = handler(factories.registry, count, dependencies=results)
        else:
            objects = create_objects(
                row, factories.registry, count, **row.get("factory_kwargs", {})
            )
        for dependency in dependencies:
            if not dependency.get("set", True):
                continue
            if create_dependencies:
                candidates = results[dependency["id"]]
            else:
                # we use existing objects in the database
                queryset = dependency.get(
                    "queryset", CONFIG_BY_ID[dependency["id"]]["model"].objects.all()
                )
                candidates = list(queryset.values_list("pk", flat=True))
                picked_pks = [random.choice(candidates) for _ in objects]
                picked_objects = {o.pk: o for o in queryset.filter(pk__in=picked_pks)}
            for i, obj in enumerate(objects):
                if create_dependencies:
                    value = random.choice(candidates)
                else:
                    value = picked_objects[picked_pks[i]]
                setattr(obj, dependency["field"], value)
        if not handler:
            objects = row["model"].objects.bulk_create(objects, batch_size=BATCH_SIZE)
        results[row["id"]] = objects
        return objects
