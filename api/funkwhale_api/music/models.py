import os
import io
import arrow
import datetime
import tempfile
import shutil
import markdown
import uuid

from django.conf import settings
from django.db import models
from django.core.files.base import ContentFile
from django.core.files import File
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone

from taggit.managers import TaggableManager
from versatileimagefield.fields import VersatileImageField

from funkwhale_api import downloader
from funkwhale_api import musicbrainz
from funkwhale_api.federation import utils as federation_utils
from . import importers
from . import metadata
from . import utils


class APIModelMixin(models.Model):
    mbid = models.UUIDField(unique=True, db_index=True, null=True, blank=True)
    uuid = models.UUIDField(
        unique=True, db_index=True, default=uuid.uuid4)
    api_includes = []
    creation_date = models.DateTimeField(default=timezone.now)
    import_hooks = []

    class Meta:
        abstract = True
        ordering = ['-creation_date']

    @classmethod
    def get_or_create_from_api(cls, mbid):
        try:
            return cls.objects.get(mbid=mbid), False
        except cls.DoesNotExist:
            return cls.create_from_api(id=mbid), True

    def get_api_data(self):
        return self.__class__.api.get(id=self.mbid, includes=self.api_includes)[self.musicbrainz_model]

    @classmethod
    def create_from_api(cls, **kwargs):
        if kwargs.get('id'):
            raw_data = cls.api.get(id=kwargs['id'], includes=cls.api_includes)[cls.musicbrainz_model]
        else:
            raw_data = cls.api.search(**kwargs)['{0}-list'.format(cls.musicbrainz_model)][0]
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
            except KeyError as e:
                pass
        return cleaned_data

    @property
    def musicbrainz_url(self):
        if self.mbid:
            return 'https://musicbrainz.org/{}/{}'.format(
                self.musicbrainz_model, self.mbid)


class ArtistQuerySet(models.QuerySet):
    def with_albums_count(self):
        return self.annotate(_albums_count=models.Count('albums'))

    def with_albums(self):
        return self.prefetch_related(
            models.Prefetch(
                'albums', queryset=Album.objects.with_tracks_count())
        )


class Artist(APIModelMixin):
    name = models.CharField(max_length=255)

    musicbrainz_model = 'artist'
    musicbrainz_mapping = {
        'mbid': {
            'musicbrainz_field_name': 'id'
        },
        'name': {
            'musicbrainz_field_name': 'name'
        }
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
        kwargs.update({'name': name})
        return cls.objects.get_or_create(
            name__iexact=name,
            defaults=kwargs)


def import_artist(v):
    a = Artist.get_or_create_from_api(mbid=v[0]['artist']['id'])[0]
    return a


def parse_date(v):
    if len(v) == 4:
        return datetime.date(int(v), 1, 1)
    d = arrow.get(v).date()
    return d


def import_tracks(instance, cleaned_data, raw_data):
    for track_data in raw_data['medium-list'][0]['track-list']:
        track_cleaned_data = Track.clean_musicbrainz_data(track_data['recording'])
        track_cleaned_data['album'] = instance
        track_cleaned_data['position'] = int(track_data['position'])
        track = importers.load(Track, track_cleaned_data, track_data, Track.import_hooks)


class AlbumQuerySet(models.QuerySet):
    def with_tracks_count(self):
        return self.annotate(_tracks_count=models.Count('tracks'))


class Album(APIModelMixin):
    title = models.CharField(max_length=255)
    artist = models.ForeignKey(
        Artist, related_name='albums', on_delete=models.CASCADE)
    release_date = models.DateField(null=True)
    release_group_id = models.UUIDField(null=True, blank=True)
    cover = VersatileImageField(upload_to='albums/covers/%Y/%m/%d', null=True, blank=True)
    TYPE_CHOICES = (
        ('album', 'Album'),
    )
    type = models.CharField(choices=TYPE_CHOICES, max_length=30, default='album')

    api_includes = ['artist-credits', 'recordings', 'media', 'release-groups']
    api = musicbrainz.api.releases
    musicbrainz_model = 'release'
    musicbrainz_mapping = {
        'mbid': {
            'musicbrainz_field_name': 'id',
        },
        'position': {
            'musicbrainz_field_name': 'release-list',
            'converter': lambda v: int(v[0]['medium-list'][0]['position']),
        },
        'release_group_id': {
            'musicbrainz_field_name': 'release-group',
            'converter': lambda v: v['id'],
        },
        'title': {
            'musicbrainz_field_name': 'title',
        },
        'release_date': {
            'musicbrainz_field_name': 'date',
            'converter': parse_date,

        },
        'type': {
            'musicbrainz_field_name': 'type',
            'converter': lambda v: v.lower(),
        },
        'artist': {
            'musicbrainz_field_name': 'artist-credit',
            'converter': import_artist,
        }
    }
    objects = AlbumQuerySet.as_manager()

    def get_image(self, data=None):
        if data:
            f = ContentFile(data['content'])
            extensions = {
                'image/jpeg': 'jpg',
                'image/png': 'png',
                'image/gif': 'gif',
            }
            extension = extensions.get(data['mimetype'], 'jpg')
            self.cover.save('{}.{}'.format(self.uuid, extension), f)
        else:
            image_data =  musicbrainz.api.images.get_front(str(self.mbid))
            f = ContentFile(image_data)
            self.cover.save('{0}.jpg'.format(self.mbid), f)
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
        kwargs.update({'title': title})
        return cls.objects.get_or_create(
            title__iexact=title,
            defaults=kwargs)


def import_tags(instance, cleaned_data, raw_data):
    MINIMUM_COUNT = 2
    tags_to_add = []
    for tag_data in raw_data.get('tag-list', []):
        try:
            if int(tag_data['count']) < MINIMUM_COUNT:
                continue
        except ValueError:
            continue
        tags_to_add.append(tag_data['name'])
    instance.tags.add(*tags_to_add)


def import_album(v):
    a = Album.get_or_create_from_api(mbid=v[0]['id'])[0]
    return a


def link_recordings(instance, cleaned_data, raw_data):
    tracks = [
        r['target']
        for r in raw_data['recording-relation-list']
    ]
    Track.objects.filter(mbid__in=tracks).update(work=instance)


def import_lyrics(instance, cleaned_data, raw_data):
    try:
        url = [
            url_data
            for url_data in raw_data['url-relation-list']
            if url_data['type'] == 'lyrics'
        ][0]['target']
    except (IndexError, KeyError):
        return
    l, _ = Lyrics.objects.get_or_create(work=instance, url=url)

    return l


class Work(APIModelMixin):
    language = models.CharField(max_length=20)
    nature = models.CharField(max_length=50)
    title = models.CharField(max_length=255)

    api = musicbrainz.api.works
    api_includes = ['url-rels', 'recording-rels']
    musicbrainz_model = 'work'
    musicbrainz_mapping = {
        'mbid': {
            'musicbrainz_field_name': 'id'
        },
        'title': {
            'musicbrainz_field_name': 'title'
        },
        'language': {
            'musicbrainz_field_name': 'language',
        },
        'nature': {
            'musicbrainz_field_name': 'type',
            'converter': lambda v: v.lower(),
        },
    }
    import_hooks = [
        import_lyrics,
        link_recordings
    ]

    def fetch_lyrics(self):
        l = self.lyrics.first()
        if l:
            return l
        data = self.api.get(self.mbid, includes=['url-rels'])['work']
        l = import_lyrics(self, {}, data)

        return l


class Lyrics(models.Model):
    uuid = models.UUIDField(
        unique=True, db_index=True, default=uuid.uuid4)
    work = models.ForeignKey(
        Work,
        related_name='lyrics',
        null=True,
        blank=True,
        on_delete=models.CASCADE)
    url = models.URLField(unique=True)
    content = models.TextField(null=True, blank=True)

    @property
    def content_rendered(self):
        return markdown.markdown(
            self.content,
            safe_mode=True,
            enable_attributes=False,
            extensions=['markdown.extensions.nl2br'])


class TrackQuerySet(models.QuerySet):
    def for_nested_serialization(self):
        return (self.select_related()
                    .select_related('album__artist', 'artist')
                    .prefetch_related('files'))


def get_artist(release_list):
    return Artist.get_or_create_from_api(
        mbid=release_list[0]['artist-credits'][0]['artists']['id'])[0]


class Track(APIModelMixin):
    title = models.CharField(max_length=255)
    artist = models.ForeignKey(
        Artist, related_name='tracks', on_delete=models.CASCADE)
    position = models.PositiveIntegerField(null=True, blank=True)
    album = models.ForeignKey(
        Album,
        related_name='tracks',
        null=True,
        blank=True,
        on_delete=models.CASCADE)
    work = models.ForeignKey(
        Work,
        related_name='tracks',
        null=True,
        blank=True,
        on_delete=models.CASCADE)

    musicbrainz_model = 'recording'
    api = musicbrainz.api.recordings
    api_includes = ['artist-credits', 'releases', 'media', 'tags', 'work-rels']
    musicbrainz_mapping = {
        'mbid': {
            'musicbrainz_field_name': 'id'
        },
        'title': {
            'musicbrainz_field_name': 'title'
        },
        'artist': {
            # we use the artist from the release to avoid #237
            'musicbrainz_field_name': 'release-list',
            'converter': get_artist,
        },
        'album': {
            'musicbrainz_field_name': 'release-list',
            'converter': import_album,
        },
    }
    import_hooks = [
        import_tags
    ]
    objects = TrackQuerySet.as_manager()
    tags = TaggableManager(blank=True)

    class Meta:
        ordering = ['album', 'position']

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
        data = self.api.get(self.mbid, includes=['work-rels'])
        try:
            work_data = data['recording']['work-relation-list'][0]['work']
        except (IndexError, KeyError):
            return
        work, _ = Work.get_or_create_from_api(mbid=work_data['id'])
        return work

    def get_lyrics_url(self):
        return reverse('api:v1:tracks-lyrics', kwargs={'pk': self.pk})

    @property
    def full_name(self):
        try:
            return '{} - {} - {}'.format(
                self.artist.name,
                self.album.title,
                self.title,
            )
        except AttributeError:
            return '{} - {}'.format(
                self.artist.name,
                self.title,
            )

    def get_activity_url(self):
        if self.mbid:
            return 'https://musicbrainz.org/recording/{}'.format(
                self.mbid)
        return settings.FUNKWHALE_URL + '/tracks/{}'.format(self.pk)

    @classmethod
    def get_or_create_from_title(cls, title, **kwargs):
        kwargs.update({'title': title})
        return cls.objects.get_or_create(
            title__iexact=title,
            defaults=kwargs)


class TrackFile(models.Model):
    uuid = models.UUIDField(
        unique=True, db_index=True, default=uuid.uuid4)
    track = models.ForeignKey(
        Track, related_name='files', on_delete=models.CASCADE)
    audio_file = models.FileField(upload_to='tracks/%Y/%m/%d', max_length=255)
    source = models.URLField(null=True, blank=True, max_length=500)
    creation_date = models.DateTimeField(default=timezone.now)
    modification_date = models.DateTimeField(auto_now=True)
    accessed_date = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    size = models.IntegerField(null=True, blank=True)
    bitrate = models.IntegerField(null=True, blank=True)
    acoustid_track_id = models.UUIDField(null=True, blank=True)
    mimetype = models.CharField(null=True, blank=True, max_length=200)

    library_track = models.OneToOneField(
        'federation.LibraryTrack',
        related_name='local_track_file',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def download_file(self):
        # import the track file, since there is not any
        # we create a tmp dir for the download
        tmp_dir = tempfile.mkdtemp()
        data = downloader.download(
            self.source,
            target_directory=tmp_dir)
        self.duration = data.get('duration', None)
        self.audio_file.save(
            os.path.basename(data['audio_file_path']),
            File(open(data['audio_file_path'], 'rb'))
        )
        shutil.rmtree(tmp_dir)
        return self.audio_file

    def get_federation_url(self):
        return federation_utils.full_url(
            '/federation/music/file/{}'.format(self.uuid)
        )

    @property
    def path(self):
        return reverse(
            'api:v1:trackfiles-serve', kwargs={'pk': self.pk})

    @property
    def filename(self):
        return '{}.{}'.format(
            self.track.full_name,
            self.extension)

    @property
    def extension(self):
        if not self.audio_file:
            return
        return os.path.splitext(self.audio_file.name)[-1].replace('.', '', 1)

    def get_file_size(self):
        if self.audio_file:
            return self.audio_file.size

        if self.source.startswith('file://'):
            return os.path.getsize(self.source.replace('file://', '', 1))

        if self.library_track and self.library_track.audio_file:
            return self.library_track.audio_file.size

    def get_audio_file(self):
        if self.audio_file:
            return self.audio_file.open()
        if self.source.startswith('file://'):
            return open(self.source.replace('file://', '', 1), 'rb')
        if self.library_track and self.library_track.audio_file:
            return self.library_track.audio_file.open()

    def set_audio_data(self):
        audio_file = self.get_audio_file()
        if audio_file:
            with audio_file as f:
                audio_data = utils.get_audio_file_data(f)
            if not audio_data:
                return
            self.duration = int(audio_data['length'])
            self.bitrate = audio_data['bitrate']
            self.size = self.get_file_size()
        else:
            lt = self.library_track
            if lt:
                self.duration = lt.get_metadata('length')
                self.size = lt.get_metadata('size')
                self.bitrate = lt.get_metadata('bitrate')

    def save(self, **kwargs):
        if not self.mimetype and self.audio_file:
            self.mimetype = utils.guess_mimetype(self.audio_file)
        return super().save(**kwargs)

    def get_metadata(self):
        audio_file = self.get_audio_file()
        if not audio_file:
            return
        return metadata.Metadata(audio_file)


IMPORT_STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('finished', 'Finished'),
    ('errored', 'Errored'),
    ('skipped', 'Skipped'),
)


class ImportBatch(models.Model):
    uuid = models.UUIDField(
        unique=True, db_index=True, default=uuid.uuid4)
    IMPORT_BATCH_SOURCES = [
        ('api', 'api'),
        ('shell', 'shell'),
        ('federation', 'federation'),
    ]
    source = models.CharField(
        max_length=30, default='api', choices=IMPORT_BATCH_SOURCES)
    creation_date = models.DateTimeField(default=timezone.now)
    submitted_by = models.ForeignKey(
        'users.User',
        related_name='imports',
        null=True,
        blank=True,
        on_delete=models.CASCADE)
    status = models.CharField(
        choices=IMPORT_STATUS_CHOICES, default='pending', max_length=30)
    import_request = models.ForeignKey(
        'requests.ImportRequest',
        related_name='import_batches',
        null=True,
        blank=True,
        on_delete=models.CASCADE)

    class Meta:
        ordering = ['-creation_date']

    def __str__(self):
        return str(self.pk)

    def update_status(self):
        old_status = self.status
        self.status = utils.compute_status(self.jobs.all())
        if self.status == old_status:
            return
        self.save(update_fields=['status'])
        if self.status != old_status and self.status == 'finished':
            from . import tasks
            tasks.import_batch_notify_followers.delay(import_batch_id=self.pk)

    def get_federation_url(self):
        return federation_utils.full_url(
            '/federation/music/import/batch/{}'.format(self.uuid)
        )


class ImportJob(models.Model):
    uuid = models.UUIDField(
        unique=True, db_index=True, default=uuid.uuid4)
    batch = models.ForeignKey(
        ImportBatch, related_name='jobs', on_delete=models.CASCADE)
    track_file = models.ForeignKey(
        TrackFile,
        related_name='jobs',
        null=True,
        blank=True,
        on_delete=models.CASCADE)
    source = models.CharField(max_length=500)
    mbid = models.UUIDField(editable=False, null=True, blank=True)

    status = models.CharField(
        choices=IMPORT_STATUS_CHOICES, default='pending', max_length=30)
    audio_file = models.FileField(
        upload_to='imports/%Y/%m/%d', max_length=255, null=True, blank=True)

    library_track = models.ForeignKey(
        'federation.LibraryTrack',
        related_name='import_jobs',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ('id', )


@receiver(post_save, sender=ImportJob)
def update_batch_status(sender, instance, **kwargs):
    instance.batch.update_status()


@receiver(post_save, sender=ImportBatch)
def update_request_status(sender, instance, created, **kwargs):
    update_fields = kwargs.get('update_fields', []) or []
    if not instance.import_request:
        return

    if not created and not 'status' in update_fields:
        return

    r_status = instance.import_request.status
    status = instance.status

    if status == 'pending' and r_status == 'pending':
        # let's mark the request as accepted since we started an import
        instance.import_request.status = 'accepted'
        return instance.import_request.save(update_fields=['status'])

    if status == 'finished' and r_status == 'accepted':
        # let's mark the request as imported since the import is over
        instance.import_request.status = 'imported'
        return instance.import_request.save(update_fields=['status'])
