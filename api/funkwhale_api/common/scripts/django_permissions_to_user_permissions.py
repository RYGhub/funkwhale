"""
Convert django permissions to user permissions in the database,
following the work done in #152.
"""
from django.db.models import Q
from funkwhale_api.users import models

from django.contrib.auth.models import Permission

mapping = {
    "dynamic_preferences.change_globalpreferencemodel": "settings",
    "music.add_importbatch": "library",
    "federation.change_library": "federation",
}


def main(command, **kwargs):
    for codename, user_permission in sorted(mapping.items()):
        app_label, c = codename.split(".")
        p = Permission.objects.get(content_type__app_label=app_label, codename=c)
        users = models.User.objects.filter(
            Q(groups__permissions=p) | Q(user_permissions=p)
        ).distinct()
        total = users.count()

        command.stdout.write(
            "Updating {} users with {} permission...".format(total, user_permission)
        )
        users.update(**{"permission_{}".format(user_permission): True})
