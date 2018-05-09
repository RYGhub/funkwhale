import collections

from django.db.models import functions, Count

from rest_framework import serializers

from funkwhale_api.music import models as music_models


def get_artist_data(artist_values):
    return {
        'id': artist_values['id'],
        'name': artist_values['name'],
        'albumCount': artist_values['_albums_count']
    }


class GetArtistsSerializer(serializers.Serializer):
    def to_representation(self, queryset):
        payload = {
            'ignoredArticles': '',
            'index': []
        }
        queryset = queryset.with_albums_count()
        queryset = queryset.order_by(functions.Lower('name'))
        values = queryset.values('id', '_albums_count', 'name')

        first_letter_mapping = collections.defaultdict(list)
        for artist in values:
            first_letter_mapping[artist['name'][0].upper()].append(artist)

        for letter, artists in sorted(first_letter_mapping.items()):
            letter_data = {
                'name': letter,
                'artist': [
                    get_artist_data(v)
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


def get_track_data(album, track, tf):
    data = {
        'id': track.pk,
        'isDir': 'false',
        'title': track.title,
        'album': album.title,
        'artist': album.artist.name,
        'track': track.position or 1,
        'contentType': tf.mimetype,
        'suffix': tf.extension or '',
        'duration': tf.duration or 0,
        'created': track.creation_date,
        'albumId': album.pk,
        'artistId': album.artist.pk,
        'type': 'music',
    }
    if album.release_date:
        data['year'] = album.release_date.year
    return data


def get_album2_data(album):
    payload = {
        'id': album.id,
        'artistId': album.artist.id,
        'name': album.title,
        'artist': album.artist.name,
        'created': album.creation_date,
    }
    try:
        payload['songCount'] = album._tracks_count
    except AttributeError:
        payload['songCount'] = len(album.tracks.prefetch_related('files'))
    return payload


def get_song_list_data(tracks):
    songs = []
    for track in tracks:
        try:
            tf = [tf for tf in track.files.all()][0]
        except IndexError:
            continue
        track_data = get_track_data(track.album, track, tf)
        songs.append(track_data)
    return songs


class GetAlbumSerializer(serializers.Serializer):
    def to_representation(self, album):
        tracks = album.tracks.prefetch_related('files').select_related('album')
        payload = get_album2_data(album)
        if album.release_date:
            payload['year'] = album.release_date.year

        payload['song'] = get_song_list_data(tracks)
        return payload


def get_starred_tracks_data(favorites):
    by_track_id = {
        f.track_id: f
        for f in favorites
    }
    tracks = music_models.Track.objects.filter(
        pk__in=by_track_id.keys()
    ).select_related('album__artist').prefetch_related('files')
    tracks = tracks.order_by('-creation_date')
    data = []
    for t in tracks:
        try:
            tf = [tf for tf in t.files.all()][0]
        except IndexError:
            continue
        td = get_track_data(t.album, t, tf)
        td['starred'] = by_track_id[t.pk].creation_date
        data.append(td)
    return data


def get_album_list2_data(albums):
    return [
        get_album2_data(a)
        for a in albums
    ]


def get_playlist_data(playlist):
    return {
        'id': playlist.pk,
        'name': playlist.name,
        'owner': playlist.user.username,
        'public': 'false',
        'songCount': playlist._tracks_count,
        'duration': 0,
        'created': playlist.creation_date,
    }


def get_playlist_detail_data(playlist):
    data = get_playlist_data(playlist)
    qs = playlist.playlist_tracks.select_related(
        'track__album__artist'
    ).prefetch_related('track__files').order_by('index')
    data['entry'] = []
    for plt in qs:
        try:
            tf = [tf for tf in plt.track.files.all()][0]
        except IndexError:
            continue
        td = get_track_data(plt.track.album, plt.track, tf)
        data['entry'].append(td)
    return data


def get_music_directory_data(artist):
    tracks = artist.tracks.select_related('album').prefetch_related('files')
    data = {
        'id': artist.pk,
        'parent': 1,
        'name': artist.name,
        'child': []
    }
    for track in tracks:
        try:
            tf = [tf for tf in track.files.all()][0]
        except IndexError:
            continue
        album = track.album
        td = {
            'id': track.pk,
            'isDir': 'false',
            'title': track.title,
            'album': album.title,
            'artist': artist.name,
            'track': track.position or 1,
            'year': track.album.release_date.year if track.album.release_date else 0,
            'contentType': tf.mimetype,
            'suffix': tf.extension or '',
            'duration': tf.duration or 0,
            'created': track.creation_date,
            'albumId': album.pk,
            'artistId': artist.pk,
            'parent': artist.id,
            'type': 'music',
        }
        data['child'].append(td)
    return data
