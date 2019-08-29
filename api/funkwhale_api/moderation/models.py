import urllib.parse
import uuid

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone

from funkwhale_api.federation import models as federation_models
from funkwhale_api.federation import utils as federation_utils


class InstancePolicyQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def matching_url(self, *urls):
        if not urls:
            return self.none()
        query = None
        for url in urls:
            new_query = self.matching_url_query(url)
            if query:
                query = query | new_query
            else:
                query = new_query
        return self.filter(query)

    def matching_url_query(self, url):
        parsed = urllib.parse.urlparse(url)
        return models.Q(target_domain_id=parsed.hostname) | models.Q(
            target_actor__fid=url
        )


class InstancePolicy(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    actor = models.ForeignKey(
        "federation.Actor",
        related_name="created_instance_policies",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    target_domain = models.OneToOneField(
        "federation.Domain",
        related_name="instance_policy",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    target_actor = models.OneToOneField(
        "federation.Actor",
        related_name="instance_policy",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    creation_date = models.DateTimeField(default=timezone.now)

    is_active = models.BooleanField(default=True)
    # a summary explaining why the policy is in place
    summary = models.TextField(max_length=10000, null=True, blank=True)
    # either block everything (simpler, but less granularity)
    block_all = models.BooleanField(default=False)
    # or pick individual restrictions below
    # do not show in timelines/notifications, except for actual followers
    silence_activity = models.BooleanField(default=False)
    silence_notifications = models.BooleanField(default=False)
    # do not download any media from the target
    reject_media = models.BooleanField(default=False)

    objects = InstancePolicyQuerySet.as_manager()

    @property
    def target(self):
        if self.target_actor:
            return {"type": "actor", "obj": self.target_actor}
        if self.target_domain_id:
            return {"type": "domain", "obj": self.target_domain}


class UserFilter(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    creation_date = models.DateTimeField(default=timezone.now)
    target_artist = models.ForeignKey(
        "music.Artist", on_delete=models.CASCADE, related_name="user_filters"
    )
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="content_filters"
    )

    class Meta:
        unique_together = ("user", "target_artist")

    @property
    def target(self):
        if self.target_artist:
            return {"type": "artist", "obj": self.target_artist}


REPORT_TYPES = [
    ("takedown_request", "Takedown request"),
    ("invalid_metadata", "Invalid metadata"),
    ("illegal_content", "Illegal content"),
    ("offensive_content", "Offensive content"),
    ("other", "Other"),
]


class Report(federation_models.FederationMixin):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    creation_date = models.DateTimeField(default=timezone.now)
    summary = models.TextField(null=True, max_length=50000)
    handled_date = models.DateTimeField(null=True)
    is_handled = models.BooleanField(default=False)
    type = models.CharField(max_length=40, choices=REPORT_TYPES)
    submitter_email = models.EmailField(null=True)
    submitter = models.ForeignKey(
        "federation.Actor",
        related_name="reports",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    assigned_to = models.ForeignKey(
        "federation.Actor",
        related_name="assigned_reports",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    target_id = models.IntegerField(null=True)
    target_content_type = models.ForeignKey(
        ContentType, null=True, on_delete=models.CASCADE
    )
    target = GenericForeignKey("target_content_type", "target_id")
    target_owner = models.ForeignKey(
        "federation.Actor", on_delete=models.SET_NULL, null=True, blank=True
    )
    # frozen state of the target being reported, to ensure we still have info in the event of a
    # delete
    target_state = JSONField(null=True)

    notes = GenericRelation(
        "Note",
        content_type_field="target_content_type",
        object_id_field="target_id",
    )

    def get_federation_id(self):
        if self.fid:
            return self.fid

        return federation_utils.full_url(
            reverse("federation:reports-detail", kwargs={"uuid": self.uuid})
        )

    def save(self, **kwargs):
        if not self.pk and not self.fid:
            self.fid = self.get_federation_id()

        return super().save(**kwargs)


class Note(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    creation_date = models.DateTimeField(default=timezone.now)
    summary = models.TextField(max_length=50000)
    author = models.ForeignKey(
        "federation.Actor", related_name="moderation_notes", on_delete=models.CASCADE
    )

    target_id = models.IntegerField(null=True)
    target_content_type = models.ForeignKey(
        ContentType, null=True, on_delete=models.CASCADE
    )
    target = GenericForeignKey("target_content_type", "target_id")


@receiver(pre_save, sender=Report)
def set_handled_date(sender, instance, **kwargs):
    if instance.is_handled is True and not instance.handled_date:
        instance.handled_date = timezone.now()
    elif not instance.is_handled:
        instance.handled_date = None
