import uuid


from django.db import models
from django.utils import timezone

from funkwhale_api.federation import keys
from funkwhale_api.federation import models as federation_models
from funkwhale_api.users import models as user_models


class Channel(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    artist = models.OneToOneField(
        "music.Artist", on_delete=models.CASCADE, related_name="channel"
    )
    # the owner of the channel
    attributed_to = models.ForeignKey(
        "federation.Actor", on_delete=models.CASCADE, related_name="owned_channels"
    )
    # the federation actor created for the channel
    # (the one people can follow to receive updates)
    actor = models.OneToOneField(
        "federation.Actor", on_delete=models.CASCADE, related_name="channel"
    )

    library = models.OneToOneField(
        "music.Library", on_delete=models.CASCADE, related_name="channel"
    )
    creation_date = models.DateTimeField(default=timezone.now)


def generate_actor(username, **kwargs):
    actor_data = user_models.get_actor_data(username, **kwargs)
    private, public = keys.get_key_pair()
    actor_data["private_key"] = private.decode("utf-8")
    actor_data["public_key"] = public.decode("utf-8")

    return federation_models.Actor.objects.create(**actor_data)
