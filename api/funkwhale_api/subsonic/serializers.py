import collections

from django.db.models import functions, Count

from rest_framework import serializers


class GetArtistsSerializer(serializers.Serializer):
    def to_representation(self, queryset):
        payload = {
            'ignoredArticles': '',
            'index': []
        }
        queryset = queryset.annotate(_albums_count=Count('albums'))
        queryset = queryset.order_by(functions.Lower('name'))
        values = queryset.values('id', '_albums_count', 'name')

        first_letter_mapping = collections.defaultdict(list)
        for artist in values:
            first_letter_mapping[artist['name'][0].upper()].append(artist)

        for letter, artists in sorted(first_letter_mapping.items()):
            letter_data = {
                'name': letter,
                'artist': [
                    {
                        'id': v['id'],
                        'name': v['name'],
                        'albumCount': v['_albums_count']
                    }
                    for v in artists
                ]
            }
            payload['index'].append(letter_data)
        return payload


class GetArtistSerializer(serializers.Serializer):
    def to_representation(self, artist):
        albums = artist.albums.prefetch_related('tracks__files')
        payload = {
            'id': artist.pk,
            'name': artist.name,
            'albumCount': len(albums),
            'album': [],
        }
        for album in albums:
            album_data = {
                'id': album.id,
                'artistId': artist.id,
                'name': album.title,
                'artist': artist.name,
                'created': album.creation_date,
                'songCount': len(album.tracks.all())
            }
            if album.release_date:
                album_data['year'] = album.release_date.year
            payload['album'].append(album_data)
        return payload


class GetAlbumSerializer(serializers.Serializer):
    def to_representation(self, album):
        tracks = album.tracks.prefetch_related('files')
        payload = {
            'id': album.id,
            'artistId': album.artist.id,
            'name': album.title,
            'artist': album.artist.name,
            'created': album.creation_date,
            'songCount': len(tracks),
            'song': [],
        }
        if album.release_date:
            payload['year'] = album.release_date.year

        for track in tracks:
            try:
                tf = [tf for tf in track.files.all()][0]
            except IndexError:
                continue
            track_data = {
                'id': track.pk,
                'isDir': False,
                'title': track.title,
                'album': album.title,
                'artist': album.artist.name,
                'track': track.position,
                'contentType': tf.mimetype,
                'suffix': tf.extension,
                'duration': tf.duration,
                'created': track.creation_date,
                'albumId': album.pk,
                'artistId': album.artist.pk,
                'type': 'music',
            }
            if album.release_date:
                track_data['year'] = album.release_date.year
            payload['song'].append(track_data)
        return payload
