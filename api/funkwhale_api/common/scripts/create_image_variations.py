"""
Compute different sizes of image used for Album covers and User avatars
"""

from versatileimagefield.image_warmer import VersatileImageFieldWarmer

from funkwhale_api.music.models import Album
from funkwhale_api.users.models import User


MODELS = [(Album, "cover", "square"), (User, "avatar", "square")]


def main(command, **kwargs):
    for model, attribute, key_set in MODELS:
        qs = model.objects.exclude(**{"{}__isnull".format(attribute): True})
        qs = qs.exclude(**{attribute: ""})
        warmer = VersatileImageFieldWarmer(
            instance_or_queryset=qs,
            rendition_key_set=key_set,
            image_attr=attribute,
            verbose=True,
        )
        command.stdout.write(
            "Creating images for {} / {}".format(model.__name__, attribute)
        )
        num_created, failed_to_create = warmer.warm()
        command.stdout.write(
            "  {} created, {} in error".format(num_created, len(failed_to_create))
        )
