import tempfile
import uuid

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils import timezone

from funkwhale_api.common import session
from funkwhale_api.common import utils as common_utils
from funkwhale_api.music import utils as music_utils

TYPE_CHOICES = [
    ("Person", "Person"),
    ("Application", "Application"),
    ("Group", "Group"),
    ("Organization", "Organization"),
    ("Service", "Service"),
]


class Actor(models.Model):
    ap_type = "Actor"

    url = models.URLField(unique=True, max_length=500, db_index=True)
    outbox_url = models.URLField(max_length=500)
    inbox_url = models.URLField(max_length=500)
    following_url = models.URLField(max_length=500, null=True, blank=True)
    followers_url = models.URLField(max_length=500, null=True, blank=True)
    shared_inbox_url = models.URLField(max_length=500, null=True, blank=True)
    type = models.CharField(choices=TYPE_CHOICES, default="Person", max_length=25)
    name = models.CharField(max_length=200, null=True, blank=True)
    domain = models.CharField(max_length=1000)
    summary = models.CharField(max_length=500, null=True, blank=True)
    preferred_username = models.CharField(max_length=200, null=True, blank=True)
    public_key = models.CharField(max_length=5000, null=True, blank=True)
    private_key = models.CharField(max_length=5000, null=True, blank=True)
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

    class Meta:
        unique_together = ["domain", "preferred_username"]

    @property
    def webfinger_subject(self):
        return "{}@{}".format(self.preferred_username, settings.FEDERATION_HOSTNAME)

    @property
    def private_key_id(self):
        return "{}#main-key".format(self.url)

    @property
    def mention_username(self):
        return "@{}@{}".format(self.preferred_username, self.domain)

    def save(self, **kwargs):
        lowercase_fields = ["domain"]
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

        return all(
            [
                settings.FEDERATION_HOSTNAME == self.domain,
                self.preferred_username in actors.SYSTEM_ACTORS,
            ]
        )

    @property
    def system_conf(self):
        from . import actors

        if self.is_system:
            return actors.SYSTEM_ACTORS[self.preferred_username]

    def get_approved_followers(self):
        follows = self.received_follows.filter(approved=True)
        return self.followers.filter(pk__in=follows.values_list("actor", flat=True))


class Follow(models.Model):
    ap_type = "Follow"

    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    actor = models.ForeignKey(
        Actor, related_name="emitted_follows", on_delete=models.CASCADE
    )
    target = models.ForeignKey(
        Actor, related_name="received_follows", on_delete=models.CASCADE
    )
    creation_date = models.DateTimeField(default=timezone.now)
    modification_date = models.DateTimeField(auto_now=True)
    approved = models.NullBooleanField(default=None)

    class Meta:
        unique_together = ["actor", "target"]

    def get_federation_url(self):
        return "{}#follows/{}".format(self.actor.url, self.uuid)


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
    metadata = JSONField(default={}, max_length=10000, encoder=DjangoJSONEncoder)

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
            verify=settings.EXTERNAL_REQUESTS_VERIFY_SSL,
            headers={"Content-Type": "application/activity+json"},
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
