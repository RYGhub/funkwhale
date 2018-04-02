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

    @property
    def webfinger_subject(self):
        return '{}@{}'.format(
            self.preferred_username,
            settings.FEDERATION_HOSTNAME,
        )

    @property
    def private_key_id(self):
        return '{}#main-key'.format(self.url)
