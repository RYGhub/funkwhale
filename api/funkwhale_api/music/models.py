import datetime
import logging
import mimetypes
import os
import tempfile
import uuid

import markdown
import pendulum
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.files.base import ContentFile
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from taggit.managers import TaggableManager

from versatileimagefield.fields import VersatileImageField
from versatileimagefield.image_warmer import VersatileImageFieldWarmer

from funkwhale_api import musicbrainz
from funkwhale_api.common import fields
from funkwhale_api.common import session
from funkwhale_api.common import utils as common_utils
from funkwhale_api.federation import models as federation_models
from funkwhale_api.federation import utils as federation_utils
from . import importers, metadata, utils

logger = logging.getLogger(__name__)


def empty_dict():
    return {}


class APIModelMixin(models.Model):
    fid = models.URLField(unique=True, max_length=500, db_index=True, null=True)
    mbid = models.UUIDField(unique=True, db_index=True, null=True, blank=True)
    uuid = models.UUIDField(unique=True, db_index=True, default=uuid.uuid4)
    from_activity = models.ForeignKey(
        "federation.Activity", null=True, blank=True, on_delete=models.SET_NULL
    )
    api_includes = []
    creation_date = models.DateTimeField(default=timezone.now)
    import_hooks = []

    class Meta:
        abstract = True
        ordering = ["-creation_date"]

    @classmethod
    def get_or_create_from_api(cls, mbid):
        try:
            return cls.objects.get(mbid=mbid), False
        except cls.DoesNotExist:
            return cls.create_from_api(id=mbid), True

    def get_api_data(self):
        return self.__class__.api.get(id=self.mbid, includes=self.api_includes)[
            self.musicbrainz_model
        ]

    @classmethod
    def create_from_api(cls, **kwargs):
        if kwargs.get("id"):
            raw_data = cls.api.get(id=kwargs["id"], includes=cls.api_includes)[
                cls.musicbrainz_model
            ]
        else:
            raw_data = cls.api.search(**kwargs)[
                "{0}-list".format(cls.musicbrainz_model)
            ][0]
        cleaned_data = cls.clean_musicbrainz_data(raw_data)
        return importers.load(cls, cleaned_data, raw_data, cls.import_hooks)

    @classmethod
    def clean_musicbrainz_data(cls, data):
        cleaned_data = {}
        mapping = importers.Mapping(cls.musicbrainz_mapping)
        for key, value in data.items():
            try:
                cleaned_key, cleaned_value = mapping.from_musicbrainz(key, value)
                cleaned_data[cleaned_key] = cleaned_value
            except KeyError:
                pass
        return cleaned_data

    @property
    def musicbrainz_url(self):
        if self.mbid:
            return "https://musicbrainz.org/{}/{}".format(
                self.musicbrainz_model, self.mbid
            )

    def get_federation_id(self):
        if self.fid:
            return self.fid

        return federation_utils.full_url(
            reverse(
                "federation:music:{}-detail".format(self.federation_namespace),
                kwargs={"uuid": self.uuid},
            )
        )

    def save(self, **kwargs):
        if not self.pk and not self.fid:
            self.fid = self.get_federation_id()

        return super().save(**kwargs)


class License(models.Model):
    code = models.CharField(primary_key=True, max_length=100)
    url = models.URLField(max_length=500)

    # if true, license is a copyleft license, meaning that derivative
    # work must be shared under the same license
    copyleft = models.BooleanField()
    # if true, commercial use of the work is allowed
    commercial = models.BooleanField()
    # if true, attribution to the original author is required when reusing
    # the work
    attribution = models.BooleanField()
    # if true, derivative work are allowed
    derivative = models.BooleanField()
    # if true, redistribution of the wor is allowed
    redistribute = models.BooleanField()

    @property
    def conf(self):
        from . import licenses

        for row in licenses.LICENSES:
            if self.code == row["code"]:
                return row
        logger.warning("%s do not match any registered license", self.code)


class ArtistQuerySet(models.QuerySet):
    def with_albums_count(self):
        return self.annotate(_albums_count=models.Count("albums"))

    def with_albums(self):
        return self.prefetch_related(
            models.Prefetch("albums", queryset=Album.objects.with_tracks_count())
        )

    def annotate_playable_by_actor(self, actor):
        tracks = (
            Upload.objects.playable_by(actor)
            .filter(track__artist=models.OuterRef("id"))
            .order_by("id")
            .values("id")[:1]
        )
        subquery = models.Subquery(tracks)
        return self.annotate(is_playable_by_actor=subquery)

    def playable_by(self, actor, include=True):
        tracks = Track.objects.playable_by(actor, include)
        if include:
            return self.filter(tracks__in=tracks).distinct()
        else:
            return self.exclude(tracks__in=tracks).distinct()


class Artist(APIModelMixin):
    name = models.CharField(max_length=255)
    federation_namespace = "artists"
    musicbrainz_model = "artist"
    musicbrainz_mapping = {
        "mbid": {"musicbrainz_field_name": "id"},
        "name": {"musicbrainz_field_name": "name"},
    }
    api = musicbrainz.api.artists
    objects = ArtistQuerySet.as_manager()

    def __str__(self):
        return self.name

    @property
    def tags(self):
        t = []
        for album in self.albums.all():
            for tag in album.tags:
                t.append(tag)
        return set(t)

    @classmethod
    def get_or_create_from_name(cls, name, **kwargs):
        kwargs.update({"name": name})
        return cls.objects.get_or_create(name__iexact=name, defaults=kwargs)


def import_artist(v):
    a = Artist.get_or_create_from_api(mbid=v[0]["artist"]["id"])[0]
    return a


def parse_date(v):
    d = pendulum.parse(v).date()
    return d


def import_tracks(instance, cleaned_data, raw_data):
    for track_data in raw_data["medium-list"][0]["track-list"]:
        track_cleaned_data = Track.clean_musicbrainz_data(track_data["recording"])
        track_cleaned_data["album"] = instance
        track_cleaned_data["position"] = int(track_data["position"])
        importers.load(Track, track_cleaned_data, track_data, Track.import_hooks)


class AlbumQuerySet(models.QuerySet):
    def with_tracks_count(self):
        return self.annotate(_tracks_count=models.Count("tracks"))

    def annotate_playable_by_actor(self, actor):
        tracks = (
            Upload.objects.playable_by(actor)
            .filter(track__album=models.OuterRef("id"))
            .order_by("id")
            .values("id")[:1]
        )
        subquery = models.Subquery(tracks)
        return self.annotate(is_playable_by_actor=subquery)

    def playable_by(self, actor, include=True):
        tracks = Track.objects.playable_by(actor, include)
        if include:
            return self.filter(tracks__in=tracks).distinct()
        else:
            return self.exclude(tracks__in=tracks).distinct()

    def with_prefetched_tracks_and_playable_uploads(self, actor):
        tracks = Track.objects.with_playable_uploads(actor)
        return self.prefetch_related(models.Prefetch("tracks", queryset=tracks))


class Album(APIModelMixin):
    title = models.CharField(max_length=255)
    artist = models.ForeignKey(Artist, related_name="albums", on_delete=models.CASCADE)
    release_date = models.DateField(null=True, blank=True)
    release_group_id = models.UUIDField(null=True, blank=True)
    cover = VersatileImageField(
        upload_to="albums/covers/%Y/%m/%d", null=True, blank=True
    )
    TYPE_CHOICES = (("album", "Album"),)
    type = models.CharField(choices=TYPE_CHOICES, max_length=30, default="album")

    api_includes = ["artist-credits", "recordings", "media", "release-groups"]
    api = musicbrainz.api.releases
    federation_namespace = "albums"
    musicbrainz_model = "release"
    musicbrainz_mapping = {
        "mbid": {"musicbrainz_field_name": "id"},
        "position": {
            "musicbrainz_field_name": "release-list",
            "converter": lambda v: int(v[0]["medium-list"][0]["position"]),
        },
        "release_group_id": {
            "musicbrainz_field_name": "release-group",
            "converter": lambda v: v["id"],
        },
        "title": {"musicbrainz_field_name": "title"},
        "release_date": {"musicbrainz_field_name": "date", "converter": parse_date},
        "type": {"musicbrainz_field_name": "type", "converter": lambda v: v.lower()},
        "artist": {
            "musicbrainz_field_name": "artist-credit",
            "converter": import_artist,
        },
    }
    objects = AlbumQuerySet.as_manager()

    def get_image(self, data=None):
        if data:
            extensions = {"image/jpeg": "jpg", "image/png": "png", "image/gif": "gif"}
            extension = extensions.get(data["mimetype"], "jpg")
            if data.get("content"):
                # we have to cover itself
                f = ContentFile(data["content"])
            elif data.get("url"):
                # we can fetch from a url
                try:
                    response = session.get_session().get(
                        data.get("url"),
                        timeout=3,
                        verify=settings.EXTERNAL_REQUESTS_VERIFY_SSL,
                    )
                    response.raise_for_status()
                except Exception as e:
                    logger.warn(
                        "Cannot download cover at url %s: %s", data.get("url"), e
                    )
                    return
                else:
                    f = ContentFile(response.content)
            self.cover.save("{}.{}".format(self.uuid, extension), f, save=False)
            self.save(update_fields=["cover"])
            return self.cover.file
        if self.mbid:
            image_data = musicbrainz.api.images.get_front(str(self.mbid))
            f = ContentFile(image_data)
            self.cover.save("{0}.jpg".format(self.mbid), f, save=False)
            self.save(update_fields=["cover"])
        return self.cover.file

    def __str__(self):
        return self.title

    @property
    def tags(self):
        t = []
        for track in self.tracks.all():
            for tag in track.tags.all():
                t.append(tag)
        return set(t)

    @classmethod
    def get_or_create_from_title(cls, title, **kwargs):
        kwargs.update({"title": title})
        return cls.objects.get_or_create(title__iexact=title, defaults=kwargs)


def import_tags(instance, cleaned_data, raw_data):
    MINIMUM_COUNT = 2
    tags_to_add = []
    for tag_data in raw_data.get("tag-list", []):
        try:
            if int(tag_data["count"]) < MINIMUM_COUNT:
                continue
        except ValueError:
            continue
        tags_to_add.append(tag_data["name"])
    instance.tags.add(*tags_to_add)


def import_album(v):
    a = Album.get_or_create_from_api(mbid=v[0]["id"])[0]
    return a


def link_recordings(instance, cleaned_data, raw_data):
    tracks = [r["target"] for r in raw_data["recording-relation-list"]]
    Track.objects.filter(mbid__in=tracks).update(work=instance)


def import_lyrics(instance, cleaned_data, raw_data):
    try:
        url = [
            url_data
            for url_data in raw_data["url-relation-list"]
            if url_data["type"] == "lyrics"
        ][0]["target"]
    except (IndexError, KeyError):
        return
    l, _ = Lyrics.objects.get_or_create(work=instance, url=url)

    return l


class Work(APIModelMixin):
    language = models.CharField(max_length=20)
    nature = models.CharField(max_length=50)
    title = models.CharField(max_length=255)

    api = musicbrainz.api.works
    api_includes = ["url-rels", "recording-rels"]
    musicbrainz_model = "work"
    federation_namespace = "works"

    musicbrainz_mapping = {
        "mbid": {"musicbrainz_field_name": "id"},
        "title": {"musicbrainz_field_name": "title"},
        "language": {"musicbrainz_field_name": "language"},
        "nature": {"musicbrainz_field_name": "type", "converter": lambda v: v.lower()},
    }
    import_hooks = [import_lyrics, link_recordings]

    def fetch_lyrics(self):
        lyric = self.lyrics.first()
        if lyric:
            return lyric
        data = self.api.get(self.mbid, includes=["url-rels"])["work"]
        lyric = import_lyrics(self, {}, data)

        return lyric

    def get_federation_id(self):
        if self.fid:
            return self.fid

        return None


class Lyrics(models.Model):
    uuid = models.UUIDField(unique=True, db_index=True, default=uuid.uuid4)
    work = models.ForeignKey(
        Work, related_name="lyrics", null=True, blank=True, on_delete=models.CASCADE
    )
    url = models.URLField(unique=True)
    content = models.TextField(null=True, blank=True)

    @property
    def content_rendered(self):
        return markdown.markdown(
            self.content,
            safe_mode=True,
            enable_attributes=False,
            extensions=["markdown.extensions.nl2br"],
        )


class TrackQuerySet(models.QuerySet):
    def for_nested_serialization(self):
        return self.select_related().select_related("album__artist", "artist")

    def annotate_playable_by_actor(self, actor):
        files = (
            Upload.objects.playable_by(actor)
            .filter(track=models.OuterRef("id"))
            .order_by("id")
            .values("id")[:1]
        )
        subquery = models.Subquery(files)
        return self.annotate(is_playable_by_actor=subquery)

    def playable_by(self, actor, include=True):
        files = Upload.objects.playable_by(actor, include)
        if include:
            return self.filter(uploads__in=files).distinct()
        else:
            return self.exclude(uploads__in=files).distinct()

    def with_playable_uploads(self, actor):
        uploads = Upload.objects.playable_by(actor).select_related("track")
        return self.prefetch_related(
            models.Prefetch("uploads", queryset=uploads, to_attr="playable_uploads")
        )

    def order_for_album(self):
        """
        Order by disc number then position
        """
        return self.order_by("disc_number", "position", "title")


def get_artist(release_list):
    return Artist.get_or_create_from_api(
        mbid=release_list[0]["artist-credits"][0]["artists"]["id"]
    )[0]


class Track(APIModelMixin):
    title = models.CharField(max_length=255)
    artist = models.ForeignKey(Artist, related_name="tracks", on_delete=models.CASCADE)
    disc_number = models.PositiveIntegerField(null=True, blank=True)
    position = models.PositiveIntegerField(null=True, blank=True)
    album = models.ForeignKey(
        Album, related_name="tracks", null=True, blank=True, on_delete=models.CASCADE
    )
    work = models.ForeignKey(
        Work, related_name="tracks", null=True, blank=True, on_delete=models.CASCADE
    )
    license = models.ForeignKey(
        License,
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name="tracks",
    )
    copyright = models.CharField(max_length=500, null=True, blank=True)
    federation_namespace = "tracks"
    musicbrainz_model = "recording"
    api = musicbrainz.api.recordings
    api_includes = ["artist-credits", "releases", "media", "tags", "work-rels"]
    musicbrainz_mapping = {
        "mbid": {"musicbrainz_field_name": "id"},
        "title": {"musicbrainz_field_name": "title"},
        "artist": {
            "musicbrainz_field_name": "artist-credit",
            "converter": lambda v: Artist.get_or_create_from_api(
                mbid=v[0]["artist"]["id"]
            )[0],
        },
        "album": {"musicbrainz_field_name": "release-list", "converter": import_album},
    }
    import_hooks = [import_tags]
    objects = TrackQuerySet.as_manager()
    tags = TaggableManager(blank=True)

    class Meta:
        ordering = ["album", "disc_number", "position"]

    def __str__(self):
        return self.title

    def save(self, **kwargs):
        try:
            self.artist
        except Artist.DoesNotExist:
            self.artist = self.album.artist
        super().save(**kwargs)

    def get_work(self):
        if self.work:
            return self.work
        data = self.api.get(self.mbid, includes=["work-rels"])
        try:
            work_data = data["recording"]["work-relation-list"][0]["work"]
        except (IndexError, KeyError):
            return
        work, _ = Work.get_or_create_from_api(mbid=work_data["id"])
        return work

    def get_lyrics_url(self):
        return reverse("api:v1:tracks-lyrics", kwargs={"pk": self.pk})

    @property
    def full_name(self):
        try:
            return "{} - {} - {}".format(self.artist.name, self.album.title, self.title)
        except AttributeError:
            return "{} - {}".format(self.artist.name, self.title)

    def get_activity_url(self):
        if self.mbid:
            return "https://musicbrainz.org/recording/{}".format(self.mbid)
        return settings.FUNKWHALE_URL + "/tracks/{}".format(self.pk)

    @classmethod
    def get_or_create_from_title(cls, title, **kwargs):
        kwargs.update({"title": title})
        return cls.objects.get_or_create(title__iexact=title, defaults=kwargs)

    @classmethod
    def get_or_create_from_release(cls, release_mbid, mbid):
        release_mbid = str(release_mbid)
        mbid = str(mbid)
        try:
            return cls.objects.get(mbid=mbid), False
        except cls.DoesNotExist:
            pass

        album = Album.get_or_create_from_api(release_mbid)[0]
        data = musicbrainz.client.api.releases.get(
            str(album.mbid), includes=Album.api_includes
        )
        tracks = [t for m in data["release"]["medium-list"] for t in m["track-list"]]
        track_data = None
        for track in tracks:
            if track["recording"]["id"] == str(mbid):
                track_data = track
                break
        if not track_data:
            raise ValueError("No track found matching this ID")

        track_artist_mbid = None
        for ac in track_data["recording"]["artist-credit"]:
            try:
                ac_mbid = ac["artist"]["id"]
            except TypeError:
                # it's probably a string, like "feat."
                continue

            if ac_mbid == str(album.artist.mbid):
                continue

            track_artist_mbid = ac_mbid
            break
        track_artist_mbid = track_artist_mbid or album.artist.mbid
        if track_artist_mbid == str(album.artist.mbid):
            track_artist = album.artist
        else:
            track_artist = Artist.get_or_create_from_api(track_artist_mbid)[0]
        return cls.objects.update_or_create(
            mbid=mbid,
            defaults={
                "position": int(track["position"]),
                "title": track["recording"]["title"],
                "album": album,
                "artist": track_artist,
            },
        )

    @property
    def listen_url(self):
        return reverse("api:v1:listen-detail", kwargs={"uuid": self.uuid})

    @property
    def local_license(self):
        """
        Since license primary keys are strings, and we can get the data
        from our hardcoded licenses.LICENSES list, there is no need
        for extra SQL joins / queries.
        """
        from . import licenses

        return licenses.LICENSES_BY_ID.get(self.license_id)


class UploadQuerySet(models.QuerySet):
    def playable_by(self, actor, include=True):
        libraries = Library.objects.viewable_by(actor)

        if include:
            return self.filter(
                library__in=libraries, import_status="finished"
            ).distinct()
        return self.exclude(library__in=libraries, import_status="finished").distinct()

    def local(self, include=True):
        return self.exclude(library__actor__user__isnull=include)

    def for_federation(self):
        return self.filter(import_status="finished", mimetype__startswith="audio/")


TRACK_FILE_IMPORT_STATUS_CHOICES = (
    ("pending", "Pending"),
    ("finished", "Finished"),
    ("errored", "Errored"),
    ("skipped", "Skipped"),
)


def get_file_path(instance, filename):
    if isinstance(instance, UploadVersion):
        return common_utils.ChunkedPath("transcoded")(instance, filename)

    if instance.library.actor.get_user():
        return common_utils.ChunkedPath("tracks")(instance, filename)
    else:
        # we cache remote tracks in a different directory
        return common_utils.ChunkedPath("federation_cache/tracks")(instance, filename)


def get_import_reference():
    return str(uuid.uuid4())


class Upload(models.Model):
    fid = models.URLField(unique=True, max_length=500, null=True, blank=True)
    uuid = models.UUIDField(unique=True, db_index=True, default=uuid.uuid4)
    track = models.ForeignKey(
        Track, related_name="uploads", on_delete=models.CASCADE, null=True, blank=True
    )
    audio_file = models.FileField(upload_to=get_file_path, max_length=255)
    source = models.CharField(
        # URL validators are not flexible enough for our file:// and upload:// schemes
        null=True,
        blank=True,
        max_length=500,
    )
    creation_date = models.DateTimeField(default=timezone.now)
    modification_date = models.DateTimeField(default=timezone.now, null=True)
    accessed_date = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    size = models.IntegerField(null=True, blank=True)
    bitrate = models.IntegerField(null=True, blank=True)
    acoustid_track_id = models.UUIDField(null=True, blank=True)
    mimetype = models.CharField(null=True, blank=True, max_length=200)
    library = models.ForeignKey(
        "library",
        null=True,
        blank=True,
        related_name="uploads",
        on_delete=models.CASCADE,
    )

    # metadata from federation
    metadata = JSONField(
        default=empty_dict, max_length=50000, encoder=DjangoJSONEncoder
    )
    import_date = models.DateTimeField(null=True, blank=True)
    # optionnal metadata provided during import
    import_metadata = JSONField(
        default=empty_dict, max_length=50000, encoder=DjangoJSONEncoder
    )
    # status / error details for the import
    import_status = models.CharField(
        default="pending", choices=TRACK_FILE_IMPORT_STATUS_CHOICES, max_length=25
    )
    # a short reference provided by the client to group multiple files
    # in the same import
    import_reference = models.CharField(max_length=50, default=get_import_reference)

    # optionnal metadata about import results (error messages, etc.)
    import_details = JSONField(
        default=empty_dict, max_length=50000, encoder=DjangoJSONEncoder
    )
    from_activity = models.ForeignKey(
        "federation.Activity", null=True, on_delete=models.SET_NULL
    )

    objects = UploadQuerySet.as_manager()

    def download_audio_from_remote(self, user):
        from funkwhale_api.common import session
        from funkwhale_api.federation import signing

        if user.is_authenticated and user.actor:
            auth = signing.get_auth(user.actor.private_key, user.actor.private_key_id)
        else:
            auth = None

        remote_response = session.get_session().get(
            self.source,
            auth=auth,
            stream=True,
            timeout=20,
            headers={"Content-Type": "application/octet-stream"},
            verify=settings.EXTERNAL_REQUESTS_VERIFY_SSL,
        )
        with remote_response as r:
            remote_response.raise_for_status()
            extension = utils.get_ext_from_type(self.mimetype)
            title = " - ".join(
                [self.track.title, self.track.album.title, self.track.artist.name]
            )
            filename = "{}.{}".format(title, extension)
            tmp_file = tempfile.TemporaryFile()
            for chunk in r.iter_content(chunk_size=512):
                tmp_file.write(chunk)
            self.audio_file.save(filename, tmp_file, save=False)
            self.save(update_fields=["audio_file"])

    def get_federation_id(self):
        if self.fid:
            return self.fid

        return federation_utils.full_url(
            reverse("federation:music:uploads-detail", kwargs={"uuid": self.uuid})
        )

    @property
    def filename(self):
        return "{}.{}".format(self.track.full_name, self.extension)

    @property
    def extension(self):
        try:
            return utils.MIMETYPE_TO_EXTENSION[self.mimetype]
        except KeyError:
            pass
        if self.audio_file:
            return os.path.splitext(self.audio_file.name)[-1].replace(".", "", 1)
        if self.in_place_path:
            return os.path.splitext(self.in_place_path)[-1].replace(".", "", 1)

    def get_file_size(self):
        if self.audio_file:
            return self.audio_file.size

        if self.source.startswith("file://"):
            return os.path.getsize(self.source.replace("file://", "", 1))

    def get_audio_file(self):
        if self.audio_file:
            return self.audio_file.open()
        if self.source.startswith("file://"):
            return open(self.source.replace("file://", "", 1), "rb")

    def get_audio_data(self):
        audio_file = self.get_audio_file()
        if not audio_file:
            return
        audio_data = utils.get_audio_file_data(audio_file)
        if not audio_data:
            return
        return {
            "duration": int(audio_data["length"]),
            "bitrate": audio_data["bitrate"],
            "size": self.get_file_size(),
        }

    def save(self, **kwargs):
        if not self.mimetype:
            if self.audio_file:
                self.mimetype = utils.guess_mimetype(self.audio_file)
            elif self.source and self.source.startswith("file://"):
                self.mimetype = mimetypes.guess_type(self.source)[0]
        if not self.size and self.audio_file:
            self.size = self.audio_file.size
        if not self.pk and not self.fid and self.library.actor.get_user():
            self.fid = self.get_federation_id()
        return super().save(**kwargs)

    def get_metadata(self):
        audio_file = self.get_audio_file()
        if not audio_file:
            return
        return metadata.Metadata(audio_file)

    @property
    def listen_url(self):
        return self.track.listen_url + "?upload={}".format(self.uuid)

    def get_transcoded_version(self, format):
        mimetype = utils.EXTENSION_TO_MIMETYPE[format]
        existing_versions = list(self.versions.filter(mimetype=mimetype))
        if existing_versions:
            # we found an existing version, no need to transcode again
            return existing_versions[0]

        return self.create_transcoded_version(mimetype, format)

    @transaction.atomic
    def create_transcoded_version(self, mimetype, format):
        # we create the version with an empty file, then
        # we'll write to it
        f = ContentFile(b"")
        version = self.versions.create(
            mimetype=mimetype, bitrate=self.bitrate or 128000, size=0
        )
        # we keep the same name, but we update the extension
        new_name = os.path.splitext(os.path.basename(self.audio_file.name))[
            0
        ] + ".{}".format(format)
        version.audio_file.save(new_name, f)
        utils.transcode_file(
            input=self.audio_file,
            output=version.audio_file,
            input_format=utils.MIMETYPE_TO_EXTENSION[self.mimetype],
            output_format=utils.MIMETYPE_TO_EXTENSION[mimetype],
        )
        version.size = version.audio_file.size
        version.save(update_fields=["size"])

        return version

    @property
    def in_place_path(self):
        if not self.source or not self.source.startswith("file://"):
            return
        return self.source.lstrip("file://")


MIMETYPE_CHOICES = [(mt, ext) for ext, mt in utils.AUDIO_EXTENSIONS_AND_MIMETYPE]


class UploadVersion(models.Model):
    upload = models.ForeignKey(
        Upload, related_name="versions", on_delete=models.CASCADE
    )
    mimetype = models.CharField(max_length=50, choices=MIMETYPE_CHOICES)
    creation_date = models.DateTimeField(default=timezone.now)
    accessed_date = models.DateTimeField(null=True, blank=True)
    audio_file = models.FileField(upload_to=get_file_path, max_length=255)
    bitrate = models.PositiveIntegerField()
    size = models.IntegerField()

    class Meta:
        unique_together = ("upload", "mimetype", "bitrate")

    @property
    def filename(self):
        return self.upload.filename


IMPORT_STATUS_CHOICES = (
    ("pending", "Pending"),
    ("finished", "Finished"),
    ("errored", "Errored"),
    ("skipped", "Skipped"),
)


class ImportBatch(models.Model):
    uuid = models.UUIDField(unique=True, db_index=True, default=uuid.uuid4)
    IMPORT_BATCH_SOURCES = [
        ("api", "api"),
        ("shell", "shell"),
        ("federation", "federation"),
    ]
    source = models.CharField(
        max_length=30, default="api", choices=IMPORT_BATCH_SOURCES
    )
    creation_date = models.DateTimeField(default=timezone.now)
    submitted_by = models.ForeignKey(
        "users.User",
        related_name="imports",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        choices=IMPORT_STATUS_CHOICES, default="pending", max_length=30
    )
    import_request = models.ForeignKey(
        "requests.ImportRequest",
        related_name="import_batches",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    library = models.ForeignKey(
        "Library",
        related_name="import_batches",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ["-creation_date"]

    def __str__(self):
        return str(self.pk)

    def update_status(self):
        old_status = self.status
        self.status = utils.compute_status(self.jobs.all())
        if self.status == old_status:
            return
        self.save(update_fields=["status"])
        if self.status != old_status and self.status == "finished":
            from . import tasks

            tasks.import_batch_notify_followers.delay(import_batch_id=self.pk)

    def get_federation_id(self):
        return federation_utils.full_url(
            "/federation/music/import/batch/{}".format(self.uuid)
        )


class ImportJob(models.Model):
    uuid = models.UUIDField(unique=True, db_index=True, default=uuid.uuid4)
    replace_if_duplicate = models.BooleanField(default=False)
    batch = models.ForeignKey(
        ImportBatch, related_name="jobs", on_delete=models.CASCADE
    )
    upload = models.ForeignKey(
        Upload, related_name="jobs", null=True, blank=True, on_delete=models.CASCADE
    )
    source = models.CharField(max_length=500)
    mbid = models.UUIDField(editable=False, null=True, blank=True)

    status = models.CharField(
        choices=IMPORT_STATUS_CHOICES, default="pending", max_length=30
    )
    audio_file = models.FileField(
        upload_to="imports/%Y/%m/%d", max_length=255, null=True, blank=True
    )

    library_track = models.ForeignKey(
        "federation.LibraryTrack",
        related_name="import_jobs",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    audio_file_size = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ("id",)

    def save(self, **kwargs):
        if self.audio_file and not self.audio_file_size:
            self.audio_file_size = self.audio_file.size
        return super().save(**kwargs)


LIBRARY_PRIVACY_LEVEL_CHOICES = [
    (k, l) for k, l in fields.PRIVACY_LEVEL_CHOICES if k != "followers"
]


class LibraryQuerySet(models.QuerySet):
    def with_follows(self, actor):
        return self.prefetch_related(
            models.Prefetch(
                "received_follows",
                queryset=federation_models.LibraryFollow.objects.filter(actor=actor),
                to_attr="_follows",
            )
        )

    def viewable_by(self, actor):
        from funkwhale_api.federation.models import LibraryFollow

        if actor is None:
            return Library.objects.filter(privacy_level="everyone")

        me_query = models.Q(privacy_level="me", actor=actor)
        instance_query = models.Q(privacy_level="instance", actor__domain=actor.domain)
        followed_libraries = LibraryFollow.objects.filter(
            actor=actor, approved=True
        ).values_list("target", flat=True)
        return Library.objects.filter(
            me_query
            | instance_query
            | models.Q(privacy_level="everyone")
            | models.Q(pk__in=followed_libraries)
        )


class Library(federation_models.FederationMixin):
    uuid = models.UUIDField(unique=True, db_index=True, default=uuid.uuid4)
    actor = models.ForeignKey(
        "federation.Actor", related_name="libraries", on_delete=models.CASCADE
    )
    followers_url = models.URLField(max_length=500)
    creation_date = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=5000, null=True, blank=True)
    privacy_level = models.CharField(
        choices=LIBRARY_PRIVACY_LEVEL_CHOICES, default="me", max_length=25
    )
    uploads_count = models.PositiveIntegerField(default=0)
    objects = LibraryQuerySet.as_manager()

    def get_federation_id(self):
        return federation_utils.full_url(
            reverse("federation:music:libraries-detail", kwargs={"uuid": self.uuid})
        )

    def save(self, **kwargs):
        if not self.pk and not self.fid and self.actor.get_user():
            self.fid = self.get_federation_id()
            self.followers_url = self.fid + "/followers"

        return super().save(**kwargs)

    def should_autoapprove_follow(self, actor):
        if self.privacy_level == "everyone":
            return True
        if self.privacy_level == "instance" and actor.get_user():
            return True
        return False

    def schedule_scan(self, actor, force=False):
        latest_scan = (
            self.scans.exclude(status="errored").order_by("-creation_date").first()
        )
        delay_between_scans = datetime.timedelta(seconds=3600 * 24)
        now = timezone.now()
        if (
            not force
            and latest_scan
            and latest_scan.creation_date + delay_between_scans > now
        ):
            return

        scan = self.scans.create(total_files=self.uploads_count, actor=actor)
        from . import tasks

        common_utils.on_commit(tasks.start_library_scan.delay, library_scan_id=scan.pk)
        return scan


SCAN_STATUS = [
    ("pending", "pending"),
    ("scanning", "scanning"),
    ("errored", "errored"),
    ("finished", "finished"),
]


class LibraryScan(models.Model):
    actor = models.ForeignKey(
        "federation.Actor", null=True, blank=True, on_delete=models.CASCADE
    )
    library = models.ForeignKey(Library, related_name="scans", on_delete=models.CASCADE)
    total_files = models.PositiveIntegerField(default=0)
    processed_files = models.PositiveIntegerField(default=0)
    errored_files = models.PositiveIntegerField(default=0)
    status = models.CharField(default="pending", max_length=25)
    creation_date = models.DateTimeField(default=timezone.now)
    modification_date = models.DateTimeField(null=True, blank=True)


@receiver(post_save, sender=ImportJob)
def update_batch_status(sender, instance, **kwargs):
    instance.batch.update_status()


@receiver(post_save, sender=ImportBatch)
def update_request_status(sender, instance, created, **kwargs):
    update_fields = kwargs.get("update_fields", []) or []
    if not instance.import_request:
        return

    if not created and "status" not in update_fields:
        return

    r_status = instance.import_request.status
    status = instance.status

    if status == "pending" and r_status == "pending":
        # let's mark the request as accepted since we started an import
        instance.import_request.status = "accepted"
        return instance.import_request.save(update_fields=["status"])

    if status == "finished" and r_status == "accepted":
        # let's mark the request as imported since the import is over
        instance.import_request.status = "imported"
        return instance.import_request.save(update_fields=["status"])


@receiver(models.signals.post_save, sender=Album)
def warm_album_covers(sender, instance, **kwargs):
    if not instance.cover:
        return
    album_covers_warmer = VersatileImageFieldWarmer(
        instance_or_queryset=instance, rendition_key_set="square", image_attr="cover"
    )
    num_created, failed_to_create = album_covers_warmer.warm()
