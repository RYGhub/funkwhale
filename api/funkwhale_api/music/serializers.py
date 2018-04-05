from django.db import transaction
from rest_framework import serializers
from taggit.models import Tag

from funkwhale_api.activity import serializers as activity_serializers

from . import models


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class SimpleArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Artist
        fields = ('id', 'mbid', 'name', 'creation_date')


class ArtistSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    class Meta:
        model = models.Artist
        fields = ('id', 'mbid', 'name', 'tags', 'creation_date')


class TrackFileSerializer(serializers.ModelSerializer):
    path = serializers.SerializerMethodField()

    class Meta:
        model = models.TrackFile
        fields = (
            'id',
            'path',
            'duration',
            'source',
            'filename',
            'mimetype',
            'track')

    def get_path(self, o):
        url = o.path
        return url


class SimpleAlbumSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Album
        fields = ('id', 'mbid', 'title', 'release_date', 'cover')


class AlbumSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    class Meta:
        model = models.Album
        fields = ('id', 'mbid', 'title', 'cover', 'release_date', 'tags')


class LyricsMixin(serializers.ModelSerializer):
    lyrics = serializers.SerializerMethodField()

    def get_lyrics(self, obj):
        return obj.get_lyrics_url()


class TrackSerializer(LyricsMixin):
    files = TrackFileSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    class Meta:
        model = models.Track
        fields = (
            'id',
            'mbid',
            'title',
            'artist',
            'files',
            'tags',
            'position',
            'lyrics')


class TrackSerializerNested(LyricsMixin):
    artist = ArtistSerializer()
    files = TrackFileSerializer(many=True, read_only=True)
    album = SimpleAlbumSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    class Meta:
        model = models.Track
        fields = ('id', 'mbid', 'title', 'artist', 'files', 'album', 'tags', 'lyrics')


class AlbumSerializerNested(serializers.ModelSerializer):
    tracks = TrackSerializer(many=True, read_only=True)
    artist = SimpleArtistSerializer()
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = models.Album
        fields = ('id', 'mbid', 'title', 'cover', 'artist', 'release_date', 'tracks', 'tags')


class ArtistSerializerNested(serializers.ModelSerializer):
    albums = AlbumSerializerNested(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    class Meta:
        model = models.Artist
        fields = ('id', 'mbid', 'name', 'albums', 'tags')


class LyricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Lyrics
        fields = ('id', 'work', 'content', 'content_rendered')


class ImportJobSerializer(serializers.ModelSerializer):
    track_file = TrackFileSerializer(read_only=True)
    class Meta:
        model = models.ImportJob
        fields = ('id', 'mbid', 'batch', 'source', 'status', 'track_file', 'audio_file')
        read_only_fields = ('status', 'track_file')


class ImportBatchSerializer(serializers.ModelSerializer):
    jobs = ImportJobSerializer(many=True, read_only=True)
    class Meta:
        model = models.ImportBatch
        fields = ('id', 'jobs', 'status', 'creation_date', 'import_request')
        read_only_fields = ('creation_date',)


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


class AudioMetadataSerializer(serializers.Serializer):
    artist = serializers.CharField(required=False)
    release = serializers.CharField(required=False)
    recording = serializers.CharField(required=False)


class AudioSerializer(serializers.Serializer):
    type = serializers.CharField()
    id = serializers.URLField()
    url = serializers.JSONField()
    metadata = AudioMetadataSerializer()

    def validate_type(self, v):
        if v != 'Audio':
            raise serializers.ValidationError('Invalid type for audio')
        return v

    def validate_url(self, v):
        try:
            url = v['href']
        except (KeyError, TypeError):
            raise serializers.ValidationError('Missing href')

        try:
            media_type = v['mediaType']
        except (KeyError, TypeError):
            raise serializers.ValidationError('Missing mediaType')

        if not media_type.startswith('audio/'):
            raise serializers.ValidationError('Invalid mediaType')

        return url

    def validate_url(self, v):
        try:
            url = v['href']
        except (KeyError, TypeError):
            raise serializers.ValidationError('Missing href')

        try:
            media_type = v['mediaType']
        except (KeyError, TypeError):
            raise serializers.ValidationError('Missing mediaType')

        if not media_type.startswith('audio/'):
            raise serializers.ValidationError('Invalid mediaType')

        return v

    def create(self, validated_data, batch):
        metadata = validated_data['metadata'].copy()
        metadata['mediaType'] = validated_data['url']['mediaType']
        return models.ImportJob.objects.create(
            batch=batch,
            source=validated_data['url']['href'],
            federation_source=validated_data['id'],
            metadata=metadata,
        )


class AudioCollectionImportSerializer(serializers.Serializer):
    id = serializers.URLField()
    items = serializers.ListField(
        child=AudioSerializer(),
        min_length=1,
    )

    @transaction.atomic
    def create(self, validated_data):
        batch = models.ImportBatch.objects.create(
            federation_actor=self.context['sender'],
            federation_source=validated_data['id'],
            source='federation',
        )
        for i in validated_data['items']:
            s = AudioSerializer(data=i)
            job = s.create(i, batch)
        return batch
