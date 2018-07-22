"""
Compute different sizes of image used for Album covers and User avatars
"""
from django.db.utils import IntegrityError

from funkwhale_api.users.models import User, create_actor


def main(command, **kwargs):
    qs = User.objects.filter(actor__isnull=True).order_by("username")
    total = len(qs)
    command.stdout.write("{} users found without actors".format(total))
    for i, user in enumerate(qs):
        command.stdout.write(
            "{}/{} creating actor for {}".format(i + 1, total, user.username)
        )
        try:
            user.actor = create_actor(user)
        except IntegrityError as e:
            # somehow, an actor with the the url exists in the database
            command.stderr.write("Error while creating actor: {}".format(str(e)))
            continue
        user.save(update_fields=["actor"])
