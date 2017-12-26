import os
import io
import arrow
import datetime
import tempfile
import shutil
import markdown

from django.conf import settings
from django.db import models
from django.core.files.base import ContentFile
from django.core.files import File
from django.urls import reverse
from django.utils import timezone
from taggit.managers import TaggableManager
from versatileimagefield.fields import VersatileImageField

from funkwhale_api import downloader
from funkwhale_api import musicbrainz
from . import importers


class APIModelMixin(models.Model):
    mbid = models.UUIDField(unique=True, db_index=True, null=True, blank=True)
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

    def __str__(self):
        return self.name

    @property
    def tags(self):
        t = []
        for album in self.albums.all():
            for tag in album.tags:
                t.append(tag)
        return set(t)

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

    def get_image(self):
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
            'musicbrainz_field_name': 'artist-credit',
            'converter': lambda v: Artist.get_or_create_from_api(mbid=v[0]['artist']['id'])[0],
        },
        'album': {
            'musicbrainz_field_name': 'release-list',
            'converter': import_album,
        },
    }
    import_hooks = [
        import_tags
    ]
    tags = TaggableManager()

    class Meta:
        ordering = ['album', 'position']

    def __str__(self):
        return self.title

    def save(self, **kwargs):
        try:
            self.artist
        except  Artist.DoesNotExist:
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


class TrackFile(models.Model):
    track = models.ForeignKey(
        Track, related_name='files', on_delete=models.CASCADE)
    audio_file = models.FileField(upload_to='tracks/%Y/%m/%d', max_length=255)
    source = models.URLField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    acoustid_track_id = models.UUIDField(null=True, blank=True)

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

    @property
    def path(self):
        if settings.PROTECT_AUDIO_FILES:
            return reverse(
                'api:v1:trackfiles-serve', kwargs={'pk': self.pk})
        return self.audio_file.url

    @property
    def filename(self):
        return '{}{}'.format(
            self.track.full_name,
            os.path.splitext(self.audio_file.name)[-1])


class ImportBatch(models.Model):
    creation_date = models.DateTimeField(default=timezone.now)
    submitted_by = models.ForeignKey(
        'users.User', related_name='imports', on_delete=models.CASCADE)

    class Meta:
        ordering = ['-creation_date']

    def __str__(self):
        return str(self.pk)

    @property
    def status(self):
        pending = any([job.status == 'pending' for job in self.jobs.all()])
        if pending:
            return 'pending'
        return 'finished'

class ImportJob(models.Model):
    batch = models.ForeignKey(
        ImportBatch, related_name='jobs', on_delete=models.CASCADE)
    track_file = models.ForeignKey(
        TrackFile,
        related_name='jobs',
        null=True,
        blank=True,
        on_delete=models.CASCADE)
    source = models.URLField()
    mbid = models.UUIDField(editable=False)
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('finished', 'finished'),
    )
    status = models.CharField(choices=STATUS_CHOICES, default='pending', max_length=30)

    class Meta:
        ordering = ('id', )
