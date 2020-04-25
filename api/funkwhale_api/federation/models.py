import tempfile
import urllib.parse
import uuid

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.urls import reverse

from funkwhale_api.common import session
from funkwhale_api.common import utils as common_utils
from funkwhale_api.common import validators as common_validators
from funkwhale_api.music import utils as music_utils

from . import utils as federation_utils

TYPE_CHOICES = [
    ("Person", "Person"),
    ("Tombstone", "Tombstone"),
    ("Application", "Application"),
    ("Group", "Group"),
    ("Organization", "Organization"),
    ("Service", "Service"),
]


def empty_dict():
    return {}


def get_shared_inbox_url():
    return federation_utils.full_url(reverse("federation:shared-inbox"))


class FederationMixin(models.Model):
    # federation id/url
    fid = models.URLField(unique=True, max_length=500, db_index=True)
    url = models.URLField(max_length=500, null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def is_local(self):
        return federation_utils.is_local(self.fid)

    @property
    def domain_name(self):
        if not self.fid:
            return

        parsed = urllib.parse.urlparse(self.fid)
        return parsed.hostname


class ActorQuerySet(models.QuerySet):
    def local(self, include=True):
        if include:
            return self.filter(domain__name=settings.FEDERATION_HOSTNAME)
        return self.exclude(domain__name=settings.FEDERATION_HOSTNAME)

    def with_current_usage(self):
        qs = self
        for s in ["draft", "pending", "skipped", "errored", "finished"]:
            uploads_query = models.Q(
                libraries__uploads__import_status=s,
                libraries__uploads__audio_file__isnull=False,
                libraries__uploads__audio_file__ne="",
            )
            qs = qs.annotate(
                **{
                    "_usage_{}".format(s): models.Sum(
                        "libraries__uploads__size", filter=uploads_query
                    )
                }
            )

        return qs

    def with_uploads_count(self):
        return self.annotate(
            uploads_count=models.Count("libraries__uploads", distinct=True)
        )


class DomainQuerySet(models.QuerySet):
    def external(self):
        return self.exclude(pk=settings.FEDERATION_HOSTNAME)

    def with_actors_count(self):
        return self.annotate(actors_count=models.Count("actors", distinct=True))

    def with_outbox_activities_count(self):
        return self.annotate(
            outbox_activities_count=models.Count(
                "actors__outbox_activities", distinct=True
            )
        )


class Domain(models.Model):
    name = models.CharField(
        primary_key=True,
        max_length=255,
        validators=[common_validators.DomainValidator()],
    )
    creation_date = models.DateTimeField(default=timezone.now)
    nodeinfo_fetch_date = models.DateTimeField(default=None, null=True, blank=True)
    nodeinfo = JSONField(default=empty_dict, max_length=50000, blank=True)
    service_actor = models.ForeignKey(
        "Actor",
        related_name="managed_domains",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    # are interactions with this domain allowed (only applies when allow-listing is on)
    allowed = models.BooleanField(default=None, null=True)

    objects = DomainQuerySet.as_manager()

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        lowercase_fields = ["name"]
        for field in lowercase_fields:
            v = getattr(self, field, None)
            if v:
                setattr(self, field, v.lower())

        super().save(**kwargs)

    def get_stats(self):
        from funkwhale_api.music import models as music_models

        data = Domain.objects.filter(pk=self.pk).aggregate(
            actors=models.Count("actors", distinct=True),
            outbox_activities=models.Count("actors__outbox_activities", distinct=True),
            libraries=models.Count("actors__libraries", distinct=True),
            channels=models.Count("actors__owned_channels", distinct=True),
            received_library_follows=models.Count(
                "actors__libraries__received_follows", distinct=True
            ),
            emitted_library_follows=models.Count(
                "actors__library_follows", distinct=True
            ),
        )
        data["artists"] = music_models.Artist.objects.filter(
            from_activity__actor__domain_id=self.pk
        ).count()
        data["albums"] = music_models.Album.objects.filter(
            from_activity__actor__domain_id=self.pk
        ).count()
        data["tracks"] = music_models.Track.objects.filter(
            from_activity__actor__domain_id=self.pk
        ).count()

        uploads = music_models.Upload.objects.filter(library__actor__domain_id=self.pk)
        data["uploads"] = uploads.count()
        data["media_total_size"] = uploads.aggregate(v=models.Sum("size"))["v"] or 0
        data["media_downloaded_size"] = (
            uploads.with_file().aggregate(v=models.Sum("size"))["v"] or 0
        )
        return data

    @property
    def is_local(self):
        return self.name == settings.FEDERATION_HOSTNAME


class Actor(models.Model):
    ap_type = "Actor"

    fid = models.URLField(unique=True, max_length=500, db_index=True)
    url = models.URLField(max_length=500, null=True, blank=True)
    outbox_url = models.URLField(max_length=500, null=True, blank=True)
    inbox_url = models.URLField(max_length=500, null=True, blank=True)
    following_url = models.URLField(max_length=500, null=True, blank=True)
    followers_url = models.URLField(max_length=500, null=True, blank=True)
    shared_inbox_url = models.URLField(max_length=500, null=True, blank=True)
    type = models.CharField(choices=TYPE_CHOICES, default="Person", max_length=25)
    name = models.CharField(max_length=200, null=True, blank=True)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name="actors")
    summary = models.CharField(max_length=500, null=True, blank=True)
    summary_obj = models.ForeignKey(
        "common.Content", null=True, blank=True, on_delete=models.SET_NULL
    )
    preferred_username = models.CharField(max_length=200, null=True, blank=True)
    public_key = models.TextField(max_length=5000, null=True, blank=True)
    private_key = models.TextField(max_length=5000, null=True, blank=True)
    creation_date = models.DateTimeField(default=timezone.now)
    last_fetch_date = models.DateTimeField(default=timezone.now)
    manually_approves_followers = models.NullBooleanField(default=None)
    followers = models.ManyToManyField(
        to="self",
        symmetrical=False,
        through="Follow",
        through_fields=("target", "actor"),
        related_name="following",
    )
    attachment_icon = models.ForeignKey(
        "common.Attachment",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="iconed_actor",
    )

    objects = ActorQuerySet.as_manager()

    class Meta:
        unique_together = ["domain", "preferred_username"]
        verbose_name = "Account"

    def get_moderation_url(self):
        return "/manage/moderation/accounts/{}".format(self.full_username)

    @property
    def webfinger_subject(self):
        return "{}@{}".format(self.preferred_username, settings.FEDERATION_HOSTNAME)

    @property
    def private_key_id(self):
        return "{}#main-key".format(self.fid)

    @property
    def full_username(self):
        return "{}@{}".format(self.preferred_username, self.domain_id)

    def __str__(self):
        return "{}@{}".format(self.preferred_username, self.domain_id)

    @property
    def is_local(self):
        return self.domain_id == settings.FEDERATION_HOSTNAME

    def get_approved_followers(self):
        follows = self.received_follows.filter(approved=True)
        return self.followers.filter(pk__in=follows.values_list("actor", flat=True))

    def should_autoapprove_follow(self, actor):
        if self.get_channel():
            return True
        return False

    def get_user(self):
        try:
            return self.user
        except ObjectDoesNotExist:
            return None

    def get_channel(self):
        try:
            return self.channel
        except ObjectDoesNotExist:
            return None

    def get_absolute_url(self):
        if self.is_local:
            return federation_utils.full_url("/@{}".format(self.preferred_username))
        return self.url or self.fid

    def get_current_usage(self):
        actor = self.__class__.objects.filter(pk=self.pk).with_current_usage().get()
        data = {}
        for s in ["draft", "pending", "skipped", "errored", "finished"]:
            data[s] = getattr(actor, "_usage_{}".format(s)) or 0

        data["total"] = sum(data.values())
        return data

    def get_stats(self):
        from funkwhale_api.music import models as music_models
        from funkwhale_api.moderation import models as moderation_models

        data = Actor.objects.filter(pk=self.pk).aggregate(
            outbox_activities=models.Count("outbox_activities", distinct=True),
            libraries=models.Count("libraries", distinct=True),
            channels=models.Count("owned_channels", distinct=True),
            received_library_follows=models.Count(
                "libraries__received_follows", distinct=True
            ),
            emitted_library_follows=models.Count("library_follows", distinct=True),
        )
        data["artists"] = music_models.Artist.objects.filter(
            from_activity__actor=self.pk
        ).count()
        data["reports"] = moderation_models.Report.objects.get_for_target(self).count()
        data["requests"] = moderation_models.UserRequest.objects.filter(
            submitter=self
        ).count()
        data["albums"] = music_models.Album.objects.filter(
            from_activity__actor=self.pk
        ).count()
        data["tracks"] = music_models.Track.objects.filter(
            from_activity__actor=self.pk
        ).count()

        uploads = music_models.Upload.objects.filter(library__actor=self.pk)
        data["uploads"] = uploads.count()
        data["media_total_size"] = uploads.aggregate(v=models.Sum("size"))["v"] or 0
        data["media_downloaded_size"] = (
            uploads.with_file().aggregate(v=models.Sum("size"))["v"] or 0
        )
        return data

    @property
    def keys(self):
        return self.private_key, self.public_key

    @keys.setter
    def keys(self, v):
        self.private_key = v[0].decode("utf-8")
        self.public_key = v[1].decode("utf-8")

    def can_manage(self, obj):
        attributed_to = getattr(obj, "attributed_to_id", None)
        if attributed_to is not None and attributed_to == self.pk:
            # easiest case, the obj is attributed to the actor
            return True

        if self.domain.service_actor_id != self.pk:
            # actor is not system actor, so there is no way the actor can manage
            # the object
            return False

        # actor is service actor of its domain, so if the fid domain
        # matches, we consider the actor has the permission to manage
        # the object
        domain = self.domain_id
        return obj.fid.startswith("http://{}/".format(domain)) or obj.fid.startswith(
            "https://{}/".format(domain)
        )

    @property
    def display_name(self):
        return self.name or self.preferred_username


FETCH_STATUSES = [
    ("pending", "Pending"),
    ("errored", "Errored"),
    ("finished", "Finished"),
    ("skipped", "Skipped"),
]


class FetchQuerySet(models.QuerySet):
    def get_for_object(self, object):
        content_type = ContentType.objects.get_for_model(object)
        return self.filter(object_content_type=content_type, object_id=object.pk)


class Fetch(models.Model):
    url = models.URLField(max_length=500, db_index=True)
    creation_date = models.DateTimeField(default=timezone.now)
    fetch_date = models.DateTimeField(null=True, blank=True)
    object_id = models.IntegerField(null=True)
    object_content_type = models.ForeignKey(
        ContentType, null=True, on_delete=models.CASCADE
    )
    object = GenericForeignKey("object_content_type", "object_id")
    status = models.CharField(default="pending", choices=FETCH_STATUSES, max_length=20)
    detail = JSONField(
        default=empty_dict, max_length=50000, encoder=DjangoJSONEncoder, blank=True
    )
    actor = models.ForeignKey(Actor, related_name="fetches", on_delete=models.CASCADE)

    objects = FetchQuerySet.as_manager()

    def save(self, **kwargs):
        if not self.url and self.object and hasattr(self.object, "fid"):
            self.url = self.object.fid

        super().save(**kwargs)

    @property
    def serializers(self):
        from . import contexts
        from . import serializers

        return {
            contexts.FW.Artist: [serializers.ArtistSerializer],
            contexts.FW.Album: [serializers.AlbumSerializer],
            contexts.FW.Track: [serializers.TrackSerializer],
            contexts.AS.Audio: [
                serializers.UploadSerializer,
                serializers.ChannelUploadSerializer,
            ],
            contexts.FW.Library: [serializers.LibrarySerializer],
            contexts.AS.Group: [serializers.ActorSerializer],
            contexts.AS.Person: [serializers.ActorSerializer],
            contexts.AS.Organization: [serializers.ActorSerializer],
            contexts.AS.Service: [serializers.ActorSerializer],
            contexts.AS.Application: [serializers.ActorSerializer],
        }


class InboxItem(models.Model):
    """
    Store activities binding to local actors, with read/unread status.
    """

    actor = models.ForeignKey(
        Actor, related_name="inbox_items", on_delete=models.CASCADE
    )
    activity = models.ForeignKey(
        "Activity", related_name="inbox_items", on_delete=models.CASCADE
    )
    type = models.CharField(max_length=10, choices=[("to", "to"), ("cc", "cc")])
    is_read = models.BooleanField(default=False)


class Delivery(models.Model):
    """
    Store deliveries attempt to remote inboxes
    """

    is_delivered = models.BooleanField(default=False)
    last_attempt_date = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveIntegerField(default=0)
    inbox_url = models.URLField(max_length=500)

    activity = models.ForeignKey(
        "Activity", related_name="deliveries", on_delete=models.CASCADE
    )


class Activity(models.Model):
    actor = models.ForeignKey(
        Actor, related_name="outbox_activities", on_delete=models.CASCADE
    )
    recipients = models.ManyToManyField(
        Actor, related_name="inbox_activities", through=InboxItem
    )
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    fid = models.URLField(unique=True, max_length=500, null=True, blank=True)
    url = models.URLField(max_length=500, null=True, blank=True)
    payload = JSONField(
        default=empty_dict, max_length=50000, encoder=DjangoJSONEncoder, blank=True
    )
    creation_date = models.DateTimeField(default=timezone.now, db_index=True)
    type = models.CharField(db_index=True, null=True, max_length=100)

    # generic relations
    object_id = models.IntegerField(null=True, blank=True)
    object_content_type = models.ForeignKey(
        ContentType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="objecting_activities",
    )
    object = GenericForeignKey("object_content_type", "object_id")
    target_id = models.IntegerField(null=True, blank=True)
    target_content_type = models.ForeignKey(
        ContentType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="targeting_activities",
    )
    target = GenericForeignKey("target_content_type", "target_id")
    related_object_id = models.IntegerField(null=True, blank=True)
    related_object_content_type = models.ForeignKey(
        ContentType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="related_objecting_activities",
    )
    related_object = GenericForeignKey(
        "related_object_content_type", "related_object_id"
    )


class AbstractFollow(models.Model):
    ap_type = "Follow"
    fid = models.URLField(unique=True, max_length=500, null=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    creation_date = models.DateTimeField(default=timezone.now)
    modification_date = models.DateTimeField(auto_now=True)
    approved = models.NullBooleanField(default=None)

    class Meta:
        abstract = True

    def get_federation_id(self):
        return federation_utils.full_url(
            "{}#follows/{}".format(self.actor.fid, self.uuid)
        )


class Follow(AbstractFollow):
    actor = models.ForeignKey(
        Actor, related_name="emitted_follows", on_delete=models.CASCADE
    )
    target = models.ForeignKey(
        Actor, related_name="received_follows", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ["actor", "target"]


class LibraryFollow(AbstractFollow):
    actor = models.ForeignKey(
        Actor, related_name="library_follows", on_delete=models.CASCADE
    )
    target = models.ForeignKey(
        "music.Library", related_name="received_follows", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ["actor", "target"]


class Library(models.Model):
    creation_date = models.DateTimeField(default=timezone.now)
    modification_date = models.DateTimeField(auto_now=True)
    fetched_date = models.DateTimeField(null=True, blank=True)
    actor = models.OneToOneField(
        Actor, on_delete=models.CASCADE, related_name="library"
    )
    uuid = models.UUIDField(default=uuid.uuid4)
    url = models.URLField(max_length=500)

    # use this flag to disable federation with a library
    federation_enabled = models.BooleanField()
    # should we mirror files locally or hotlink them?
    download_files = models.BooleanField()
    # should we automatically import new files from this library?
    autoimport = models.BooleanField()
    tracks_count = models.PositiveIntegerField(null=True, blank=True)
    follow = models.OneToOneField(
        Follow, related_name="library", null=True, blank=True, on_delete=models.SET_NULL
    )


get_file_path = common_utils.ChunkedPath("federation_cache")


class LibraryTrack(models.Model):
    url = models.URLField(unique=True, max_length=500)
    audio_url = models.URLField(max_length=500)
    audio_mimetype = models.CharField(max_length=200)
    audio_file = models.FileField(upload_to=get_file_path, null=True, blank=True)

    creation_date = models.DateTimeField(default=timezone.now)
    modification_date = models.DateTimeField(auto_now=True)
    fetched_date = models.DateTimeField(null=True, blank=True)
    published_date = models.DateTimeField(null=True, blank=True)
    library = models.ForeignKey(
        Library, related_name="tracks", on_delete=models.CASCADE
    )
    artist_name = models.CharField(max_length=500)
    album_title = models.CharField(max_length=500)
    title = models.CharField(max_length=500)
    metadata = JSONField(
        default=empty_dict, max_length=10000, encoder=DjangoJSONEncoder, blank=True
    )

    @property
    def mbid(self):
        try:
            return self.metadata["recording"]["musicbrainz_id"]
        except KeyError:
            pass

    def download_audio(self):
        from . import actors

        auth = actors.SYSTEM_ACTORS["library"].get_request_auth()
        remote_response = session.get_session().get(
            self.audio_url,
            auth=auth,
            stream=True,
            timeout=20,
            headers={"Accept": "application/activity+json"},
        )
        with remote_response as r:
            remote_response.raise_for_status()
            extension = music_utils.get_ext_from_type(self.audio_mimetype)
            title = " - ".join([self.title, self.album_title, self.artist_name])
            filename = "{}.{}".format(title, extension)
            tmp_file = tempfile.TemporaryFile()
            for chunk in r.iter_content(chunk_size=512):
                tmp_file.write(chunk)
            self.audio_file.save(filename, tmp_file)

    def get_metadata(self, key):
        return self.metadata.get(key)


@receiver(pre_save, sender=LibraryFollow)
def set_approved_updated(sender, instance, update_fields, **kwargs):
    if not instance.pk or not instance.actor.is_local:
        return
    if update_fields is not None and "approved" not in update_fields:
        return
    db_value = instance.__class__.objects.filter(pk=instance.pk).values_list(
        "approved", flat=True
    )[0]
    if db_value != instance.approved:
        # Needed to update denormalized permissions
        setattr(instance, "_approved_updated", True)


@receiver(post_save, sender=LibraryFollow)
def update_denormalization_follow_approved(sender, instance, created, **kwargs):
    from funkwhale_api.music import models as music_models

    updated = getattr(instance, "_approved_updated", False)

    if (created or updated) and instance.actor.is_local:
        music_models.TrackActor.create_entries(
            instance.target,
            actor_ids=[instance.actor.pk],
            delete_existing=not instance.approved,
        )


@receiver(post_delete, sender=LibraryFollow)
def update_denormalization_follow_deleted(sender, instance, **kwargs):
    from funkwhale_api.music import models as music_models

    if instance.actor.is_local:
        music_models.TrackActor.objects.filter(
            actor=instance.actor, upload__in=instance.target.uploads.all()
        ).delete()
