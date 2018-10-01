"""
Mirate instance files to a library #463. For each user that imported music on an
instance, we will create a "default" library with related files and an instance-level
visibility (unless instance has common__api_authentication_required set to False,
in which case the libraries will be public).

Files without any import job will be bounded to a "default" library on the first
superuser account found. This should now happen though.

This command will also generate federation ids for existing resources.

"""

from django.conf import settings
from django.db.models import functions, CharField, F, Value

from funkwhale_api.music import models
from funkwhale_api.users.models import User
from funkwhale_api.federation import models as federation_models
from funkwhale_api.common import preferences


def create_libraries(open_api, stdout):
    local_actors = federation_models.Actor.objects.exclude(user=None).only("pk", "user")
    privacy_level = "everyone" if open_api else "instance"
    stdout.write(
        "* Creating {} libraries with {} visibility".format(
            len(local_actors), privacy_level
        )
    )
    libraries_by_user = {}

    for a in local_actors:
        library, created = models.Library.objects.get_or_create(
            name="default", actor=a, defaults={"privacy_level": privacy_level}
        )
        libraries_by_user[library.actor.user.pk] = library.pk
        if created:
            stdout.write(
                "  * Created library {} for user {}".format(library.pk, a.user.pk)
            )
        else:
            stdout.write(
                "  * Found existing library {} for user {}".format(
                    library.pk, a.user.pk
                )
            )

    return libraries_by_user


def update_uploads(libraries_by_user, stdout):
    stdout.write("* Updating uploads with proper libraries...")
    for user_id, library_id in libraries_by_user.items():
        jobs = models.ImportJob.objects.filter(
            upload__library=None, batch__submitted_by=user_id
        )
        candidates = models.Upload.objects.filter(
            pk__in=jobs.values_list("upload", flat=True)
        )
        total = candidates.update(library=library_id, import_status="finished")
        if total:
            stdout.write(
                "  * Assigned {} uploads to user {}'s library".format(total, user_id)
            )
        else:
            stdout.write(
                "  * No uploads to assign to user {}'s library".format(user_id)
            )


def update_orphan_uploads(open_api, stdout):
    privacy_level = "everyone" if open_api else "instance"
    first_superuser = (
        User.objects.filter(is_superuser=True)
        .exclude(actor=None)
        .order_by("pk")
        .first()
    )
    if not first_superuser:
        stdout.write("* No superuser found, skipping update orphan uploads")
        return
    library, _ = models.Library.objects.get_or_create(
        name="default",
        actor=first_superuser.actor,
        defaults={"privacy_level": privacy_level},
    )
    candidates = (
        models.Upload.objects.filter(library=None, jobs__isnull=True)
        .exclude(audio_file=None)
        .exclude(audio_file="")
    )

    total = candidates.update(library=library, import_status="finished")
    if total:
        stdout.write(
            "* Assigned {} orphaned uploads to superuser {}".format(
                total, first_superuser.pk
            )
        )
    else:
        stdout.write("* No orphaned uploads found")


def set_fid(queryset, path, stdout):
    model = queryset.model._meta.label
    qs = queryset.filter(fid=None)
    base_url = "{}{}".format(settings.FUNKWHALE_URL, path)
    stdout.write(
        "* Assigning federation ids to {} entries (path: {})".format(model, base_url)
    )
    new_fid = functions.Concat(Value(base_url), F("uuid"), output_field=CharField())
    total = qs.update(fid=new_fid)

    stdout.write("  * {} entries updated".format(total))


def update_shared_inbox_url(stdout):
    stdout.write("* Update shared inbox url for local actors...")
    candidates = federation_models.Actor.objects.local()
    url = federation_models.get_shared_inbox_url()
    candidates.update(shared_inbox_url=url)


def generate_actor_urls(part, stdout):
    field = "{}_url".format(part)
    stdout.write("* Update {} for local actors...".format(field))

    queryset = federation_models.Actor.objects.local().filter(**{field: None})
    base_url = "{}/federation/actors/".format(settings.FUNKWHALE_URL)

    new_field = functions.Concat(
        Value(base_url),
        F("preferred_username"),
        Value("/{}".format(part)),
        output_field=CharField(),
    )

    queryset.update(**{field: new_field})


def main(command, **kwargs):
    open_api = not preferences.get("common__api_authentication_required")
    libraries_by_user = create_libraries(open_api, command.stdout)
    update_uploads(libraries_by_user, command.stdout)
    update_orphan_uploads(open_api, command.stdout)

    set_fid_params = [
        (
            models.Upload.objects.exclude(library__actor__user=None),
            "/federation/music/uploads/",
        ),
        (models.Artist.objects.all(), "/federation/music/artists/"),
        (models.Album.objects.all(), "/federation/music/albums/"),
        (models.Track.objects.all(), "/federation/music/tracks/"),
    ]
    for qs, path in set_fid_params:
        set_fid(qs, path, command.stdout)

    update_shared_inbox_url(command.stdout)

    for part in ["followers", "following"]:
        generate_actor_urls(part, command.stdout)
