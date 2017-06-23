from rest_framework import serializers
from taggit.models import Tag

from . import models


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')

class SimpleArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Artist
        fields = ('id', 'mbid', 'name')

class ArtistSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    class Meta:
        model = models.Artist
        fields = ('id', 'mbid', 'name', 'tags')

class ImportJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ImportJob
        fields = ('id', 'mbid', 'source', 'status')

class ImportBatchSerializer(serializers.ModelSerializer):
    jobs = ImportJobSerializer(many=True, read_only=True)
    class Meta:
        model = models.ImportBatch
        fields = ('id', 'jobs', 'status', 'creation_date')

class TrackFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TrackFile
        fields = ('id', 'path', 'duration', 'source')


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
        fields = ('id', 'mbid', 'title', 'artist', 'files', 'tags', 'lyrics')

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
