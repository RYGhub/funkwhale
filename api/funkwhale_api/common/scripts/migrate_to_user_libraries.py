"""
Mirate instance files to a library #463. For each user that imported music on an
instance, we will create a "default" library with related files and an instance-level
visibility.

Files without any import job will be bounded to a "default" library on the first
superuser account found. This should now happen though.

XXX TODO:

- add followers url on actor
- shared inbox url on actor
- compute hash from files
"""

from funkwhale_api.music import models
from funkwhale_api.users.models import User


def main(command, **kwargs):
    importer_ids = set(
        models.ImportBatch.objects.values_list("submitted_by", flat=True)
    )
    importers = User.objects.filter(pk__in=importer_ids).order_by("id").select_related()
    command.stdout.write(
        "* {} users imported music on this instance".format(len(importers))
    )
    files = models.Upload.objects.filter(
        library__isnull=True, jobs__isnull=False
    ).distinct()
    command.stdout.write(
        "* Reassigning {} files to importers libraries...".format(files.count())
    )
    for user in importers:
        command.stdout.write(
            "  * Setting up @{}'s 'default' library".format(user.username)
        )
        library = user.actor.libraries.get_or_create(actor=user.actor, name="default")[
            0
        ]
        user_files = files.filter(jobs__batch__submitted_by=user)
        total = user_files.count()
        command.stdout.write(
            "    * Reassigning {} files to the user library...".format(total)
        )
        user_files.update(library=library)

    files = models.Upload.objects.filter(
        library__isnull=True, jobs__isnull=True
    ).distinct()
    command.stdout.write(
        "* Handling {} files with no import jobs...".format(files.count())
    )

    user = User.objects.order_by("id").filter(is_superuser=True).first()

    command.stdout.write("  * Setting up @{}'s 'default' library".format(user.username))
    library = user.actor.libraries.get_or_create(actor=user.actor, name="default")[0]
    total = files.count()
    command.stdout.write(
        "    * Reassigning {} files to the user library...".format(total)
    )
    files.update(library=library)
    command.stdout.write(" * Done!")
