import uuid


from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.db.models.signals import post_delete
from django.dispatch import receiver

from funkwhale_api.federation import keys
from funkwhale_api.federation import models as federation_models
from funkwhale_api.federation import utils as federation_utils
from funkwhale_api.users import models as user_models


def empty_dict():
    return {}


class ChannelQuerySet(models.QuerySet):
    def external_rss(self, include=True):
        from funkwhale_api.federation import actors

        query = models.Q(
            attributed_to=actors.get_service_actor(),
            actor__preferred_username__startswith="rssfeed-",
        )
        if include:
            return self.filter(query)
        return self.exclude(query)

    def subscribed(self, actor):
        if not actor:
            return self.none()

        subscriptions = actor.emitted_follows.filter(
            approved=True, target__channel__isnull=False
        )
        return self.filter(actor__in=subscriptions.values_list("target", flat=True))


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
    rss_url = models.URLField(max_length=500, null=True, blank=True)

    # metadata to enhance rss feed
    metadata = JSONField(
        default=empty_dict, max_length=50000, encoder=DjangoJSONEncoder, blank=True
    )

    fetches = GenericRelation(
        "federation.Fetch",
        content_type_field="object_content_type",
        object_id_field="object_id",
    )
    objects = ChannelQuerySet.as_manager()

    @property
    def fid(self):
        if not self.is_external_rss:
            return self.actor.fid

    @property
    def is_local(self):
        return self.actor.is_local

    @property
    def is_external_rss(self):
        return self.actor.preferred_username.startswith("rssfeed-")

    def get_absolute_url(self):
        suffix = self.uuid
        if self.actor.is_local:
            suffix = self.actor.preferred_username
        else:
            suffix = self.actor.full_username
        return federation_utils.full_url("/channels/{}".format(suffix))

    def get_rss_url(self):
        if not self.artist.is_local or self.is_external_rss:
            return self.rss_url

        return federation_utils.full_url(
            reverse(
                "api:v1:channels-rss",
                kwargs={"composite": self.actor.preferred_username},
            )
        )


def generate_actor(username, **kwargs):
    actor_data = user_models.get_actor_data(username, **kwargs)
    private, public = keys.get_key_pair()
    actor_data["private_key"] = private.decode("utf-8")
    actor_data["public_key"] = public.decode("utf-8")

    return federation_models.Actor.objects.create(**actor_data)


@receiver(post_delete, sender=Channel)
def delete_channel_related_objs(instance, **kwargs):
    instance.library.delete()
    instance.artist.delete()
