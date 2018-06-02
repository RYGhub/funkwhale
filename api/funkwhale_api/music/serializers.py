from django.db import transaction
from django.db.models import Q
from rest_framework import serializers
from taggit.models import Tag

from funkwhale_api.activity import serializers as activity_serializers
from funkwhale_api.federation import utils as federation_utils
from funkwhale_api.federation.models import LibraryTrack
from funkwhale_api.federation.serializers import AP_CONTEXT
from funkwhale_api.users.serializers import UserBasicSerializer

from . import models
from . import tasks


class ArtistAlbumSerializer(serializers.ModelSerializer):
    tracks_count = serializers.SerializerMethodField()

    class Meta:
        model = models.Album
        fields = (
            'id',
            'mbid',
            'title',
            'artist',
            'release_date',
            'cover',
            'creation_date',
            'tracks_count',
        )

    def get_tracks_count(self, o):
        return o._tracks_count


class ArtistWithAlbumsSerializer(serializers.ModelSerializer):
    albums = ArtistAlbumSerializer(many=True, read_only=True)

    class Meta:
        model = models.Artist
        fields = (
            'id',
            'mbid',
            'name',
            'creation_date',
            'albums',
        )


class TrackFileSerializer(serializers.ModelSerializer):
    path = serializers.SerializerMethodField()

    class Meta:
        model = models.TrackFile
        fields = (
            'id',
            'path',
            'source',
            'filename',
            'mimetype',
            'track',
            'duration',
            'mimetype',
            'bitrate',
            'size',
        )
        read_only_fields = [
            'duration',
            'mimetype',
            'bitrate',
            'size',
        ]

    def get_path(self, o):
        url = o.path
        return url


class AlbumTrackSerializer(serializers.ModelSerializer):
    files = TrackFileSerializer(many=True, read_only=True)

    class Meta:
        model = models.Track
        fields = (
            'id',
            'mbid',
            'title',
            'album',
            'artist',
            'creation_date',
            'files',
            'position',
        )


class ArtistSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Artist
        fields = (
            'id',
            'mbid',
            'name',
            'creation_date',
        )


class AlbumSerializer(serializers.ModelSerializer):
    tracks = serializers.SerializerMethodField()
    artist = ArtistSimpleSerializer(read_only=True)

    class Meta:
        model = models.Album
        fields = (
            'id',
            'mbid',
            'title',
            'artist',
            'tracks',
            'release_date',
            'cover',
            'creation_date',
        )

    def get_tracks(self, o):
        ordered_tracks = sorted(
            o.tracks.all(),
            key=lambda v: (v.position, v.title) if v.position else (99999, v.title)
        )
        return AlbumTrackSerializer(ordered_tracks, many=True).data


class TrackAlbumSerializer(serializers.ModelSerializer):
    artist = ArtistSimpleSerializer(read_only=True)

    class Meta:
        model = models.Album
        fields = (
            'id',
            'mbid',
            'title',
            'artist',
            'release_date',
            'cover',
            'creation_date',
        )


class TrackSerializer(serializers.ModelSerializer):
    files = TrackFileSerializer(many=True, read_only=True)
    artist = ArtistSimpleSerializer(read_only=True)
    album = TrackAlbumSerializer(read_only=True)
    lyrics = serializers.SerializerMethodField()

    class Meta:
        model = models.Track
        fields = (
            'id',
            'mbid',
            'title',
            'album',
            'artist',
            'creation_date',
            'files',
            'position',
            'lyrics',
        )

    def get_lyrics(self, obj):
        return obj.get_lyrics_url()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class SimpleAlbumSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Album
        fields = ('id', 'mbid', 'title', 'release_date', 'cover')


class LyricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Lyrics
        fields = ('id', 'work', 'content', 'content_rendered')


class ImportJobSerializer(serializers.ModelSerializer):
    track_file = TrackFileSerializer(read_only=True)

    class Meta:
        model = models.ImportJob
        fields = (
            'id',
            'mbid',
            'batch',
            'source',
            'status',
            'track_file',
            'audio_file')
        read_only_fields = ('status', 'track_file')


class ImportBatchSerializer(serializers.ModelSerializer):
    submitted_by = UserBasicSerializer(read_only=True)

    class Meta:
        model = models.ImportBatch
        fields = (
            'id',
            'submitted_by',
            'source',
            'status',
            'creation_date',
            'import_request')
        read_only_fields = (
            'creation_date', 'submitted_by', 'source')

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        try:
            repr['job_count'] = instance.job_count
        except AttributeError:
            # Queryset was not annotated
            pass
        return repr


class TrackActivitySerializer(activity_serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    name = serializers.CharField(source='title')
    artist = serializers.CharField(source='artist.name')
    album = serializers.CharField(source='album.title')

    class Meta:
        model = models.Track
        fields = [
            'id',
            'local_id',
            'name',
            'type',
            'artist',
            'album',
        ]

    def get_type(self, obj):
        return 'Audio'


class ImportJobRunSerializer(serializers.Serializer):
    jobs = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=models.ImportJob.objects.filter(
            status__in=['pending', 'errored']
        )
    )
    batches = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=models.ImportBatch.objects.all()
    )

    def validate(self, validated_data):
        jobs = validated_data['jobs']
        batches_ids = [b.pk for b in validated_data['batches']]
        query = Q(batch__pk__in=batches_ids)
        query |= Q(pk__in=[j.id for j in jobs])
        queryset = models.ImportJob.objects.filter(query).filter(
            status__in=['pending', 'errored']).distinct()
        validated_data['_jobs'] = queryset
        return validated_data

    def create(self, validated_data):
        ids = validated_data['_jobs'].values_list('id', flat=True)
        validated_data['_jobs'].update(status='pending')
        for id in ids:
            tasks.import_job_run.delay(import_job_id=id)
        return {'jobs': list(ids)}
