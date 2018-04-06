import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

TYPE_CHOICES = [
    ('Person', 'Person'),
    ('Application', 'Application'),
    ('Group', 'Group'),
    ('Organization', 'Organization'),
    ('Service', 'Service'),
]


class Actor(models.Model):
    ap_type = 'Actor'

    url = models.URLField(unique=True, max_length=500, db_index=True)
    outbox_url = models.URLField(max_length=500)
    inbox_url = models.URLField(max_length=500)
    following_url = models.URLField(max_length=500, null=True, blank=True)
    followers_url = models.URLField(max_length=500, null=True, blank=True)
    shared_inbox_url = models.URLField(max_length=500, null=True, blank=True)
    type = models.CharField(
        choices=TYPE_CHOICES, default='Person', max_length=25)
    name = models.CharField(max_length=200, null=True, blank=True)
    domain = models.CharField(max_length=1000)
    summary = models.CharField(max_length=500, null=True, blank=True)
    preferred_username = models.CharField(
        max_length=200, null=True, blank=True)
    public_key = models.CharField(max_length=5000, null=True, blank=True)
    private_key = models.CharField(max_length=5000, null=True, blank=True)
    creation_date = models.DateTimeField(default=timezone.now)
    last_fetch_date = models.DateTimeField(
        default=timezone.now)
    manually_approves_followers = models.NullBooleanField(default=None)
    followers = models.ManyToManyField(
        to='self',
        symmetrical=False,
        through='Follow',
        through_fields=('target', 'actor'),
        related_name='following',
    )

    class Meta:
        unique_together = ['domain', 'preferred_username']

    @property
    def webfinger_subject(self):
        return '{}@{}'.format(
            self.preferred_username,
            settings.FEDERATION_HOSTNAME,
        )

    @property
    def private_key_id(self):
        return '{}#main-key'.format(self.url)

    @property
    def mention_username(self):
        return '@{}@{}'.format(self.preferred_username, self.domain)

    def save(self, **kwargs):
        lowercase_fields = [
            'domain',
        ]
        for field in lowercase_fields:
            v = getattr(self, field, None)
            if v:
                setattr(self, field, v.lower())

        super().save(**kwargs)

    @property
    def is_local(self):
        return self.domain == settings.FEDERATION_HOSTNAME

    @property
    def is_system(self):
        from . import actors
        return all([
            settings.FEDERATION_HOSTNAME == self.domain,
            self.preferred_username in actors.SYSTEM_ACTORS
        ])

    @property
    def system_conf(self):
        from . import actors
        if self.is_system:
            return actors.SYSTEM_ACTORS[self.preferred_username]


class Follow(models.Model):
    ap_type = 'Follow'

    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    actor = models.ForeignKey(
        Actor,
        related_name='emitted_follows',
        on_delete=models.CASCADE,
    )
    target = models.ForeignKey(
        Actor,
        related_name='received_follows',
        on_delete=models.CASCADE,
    )
    creation_date = models.DateTimeField(default=timezone.now)
    modification_date = models.DateTimeField(
        auto_now=True)

    class Meta:
        unique_together = ['actor', 'target']

    def get_federation_url(self):
        return '{}#follows/{}'.format(self.actor.url, self.uuid)


class FollowRequest(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    actor = models.ForeignKey(
        Actor,
        related_name='emmited_follow_requests',
        on_delete=models.CASCADE,
    )
    target = models.ForeignKey(
        Actor,
        related_name='received_follow_requests',
        on_delete=models.CASCADE,
    )
    creation_date = models.DateTimeField(default=timezone.now)
    modification_date = models.DateTimeField(
        auto_now=True)
    approved = models.NullBooleanField(default=None)

    def approve(self):
        from . import activity
        from . import serializers
        self.approved = True
        self.save(update_fields=['approved'])
        Follow.objects.get_or_create(
            target=self.target,
            actor=self.actor
        )
        if self.target.is_local:
            follow = {
                '@context': serializers.AP_CONTEXT,
                'actor': self.actor.url,
                'id': self.actor.url + '#follows/{}'.format(uuid.uuid4()),
                'object': self.target.url,
                'type': 'Follow'
            }
            activity.accept_follow(
                self.target, follow, self.actor
            )

    def refuse(self):
        self.approved = False
        self.save(update_fields=['approved'])
