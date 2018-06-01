from funkwhale_api.music import models as music_models
from funkwhale_api.subsonic import serializers


def test_get_artists_serializer(factories):
    artist1 = factories['music.Artist'](name='eliot')
    artist2 = factories['music.Artist'](name='Ellena')
    artist3 = factories['music.Artist'](name='Rilay')

    factories['music.Album'].create_batch(size=3, artist=artist1)
    factories['music.Album'].create_batch(size=2, artist=artist2)

    expected = {
        'ignoredArticles': '',
        'index': [
            {
                'name': 'E',
                'artist': [
                    {
                        'id': artist1.pk,
                        'name': artist1.name,
                        'albumCount': 3,
                    },
                    {
                        'id': artist2.pk,
                        'name': artist2.name,
                        'albumCount': 2,
                    },
                ]
            },
            {
                'name': 'R',
                'artist': [
                    {
                        'id': artist3.pk,
                        'name': artist3.name,
                        'albumCount': 0,
                    },
                ]
            },
        ]
    }

    queryset = artist1.__class__.objects.filter(pk__in=[
        artist1.pk, artist2.pk, artist3.pk
    ])

    assert serializers.GetArtistsSerializer(queryset).data == expected


def test_get_artist_serializer(factories):
    artist = factories['music.Artist']()
    album = factories['music.Album'](artist=artist)
    tracks = factories['music.Track'].create_batch(size=3, album=album)

    expected = {
        'id': artist.pk,
        'name': artist.name,
        'albumCount': 1,
        'album': [
            {
                'id': album.pk,
                'coverArt': 'al-{}'.format(album.id),
                'artistId': artist.pk,
                'name': album.title,
                'artist': artist.name,
                'songCount': len(tracks),
                'created': album.creation_date,
                'year': album.release_date.year,
            }
        ]
    }

    assert serializers.GetArtistSerializer(artist).data == expected


def test_get_album_serializer(factories):
    artist = factories['music.Artist']()
    album = factories['music.Album'](artist=artist)
    track = factories['music.Track'](album=album)
    tf = factories['music.TrackFile'](
        track=track, bitrate=42000, duration=43, size=44)

    expected = {
        'id': album.pk,
        'artistId': artist.pk,
        'name': album.title,
        'artist': artist.name,
        'songCount': 1,
        'created': album.creation_date,
        'year': album.release_date.year,
        'coverArt': 'al-{}'.format(album.id),
        'song': [
            {
                'id': track.pk,
                'isDir': 'false',
                'title': track.title,
                'coverArt': 'al-{}'.format(album.id),
                'album': album.title,
                'artist': artist.name,
                'track': track.position,
                'year': track.album.release_date.year,
                'contentType': tf.mimetype,
                'suffix': tf.extension or '',
                'bitrate': 42,
                'duration': 43,
                'size': 44,
                'created': track.creation_date,
                'albumId': album.pk,
                'artistId': artist.pk,
                'type': 'music',
            }
        ]
    }

    assert serializers.GetAlbumSerializer(album).data == expected


def test_starred_tracks2_serializer(factories):
    artist = factories['music.Artist']()
    album = factories['music.Album'](artist=artist)
    track = factories['music.Track'](album=album)
    tf = factories['music.TrackFile'](track=track)
    favorite = factories['favorites.TrackFavorite'](track=track)
    expected = [serializers.get_track_data(album, track, tf)]
    expected[0]['starred'] = favorite.creation_date
    data = serializers.get_starred_tracks_data([favorite])
    assert data == expected


def test_get_album_list2_serializer(factories):
    album1 = factories['music.Album']()
    album2 = factories['music.Album']()

    qs = music_models.Album.objects.with_tracks_count().order_by('pk')
    expected = [
        serializers.get_album2_data(album1),
        serializers.get_album2_data(album2),
    ]
    data = serializers.get_album_list2_data(qs)
    assert data == expected


def test_playlist_serializer(factories):
    plt = factories['playlists.PlaylistTrack']()
    playlist = plt.playlist
    qs = music_models.Album.objects.with_tracks_count().order_by('pk')
    expected = {
        'id': playlist.pk,
        'name': playlist.name,
        'owner': playlist.user.username,
        'public': 'false',
        'songCount': 1,
        'duration': 0,
        'created': playlist.creation_date,
    }
    qs = playlist.__class__.objects.with_tracks_count()
    data = serializers.get_playlist_data(qs.first())
    assert data == expected


def test_playlist_detail_serializer(factories):
    plt = factories['playlists.PlaylistTrack']()
    tf = factories['music.TrackFile'](track=plt.track)
    playlist = plt.playlist
    qs = music_models.Album.objects.with_tracks_count().order_by('pk')
    expected = {
        'id': playlist.pk,
        'name': playlist.name,
        'owner': playlist.user.username,
        'public': 'false',
        'songCount': 1,
        'duration': 0,
        'created': playlist.creation_date,
        'entry': [
            serializers.get_track_data(plt.track.album, plt.track, tf)
        ]
    }
    qs = playlist.__class__.objects.with_tracks_count()
    data = serializers.get_playlist_detail_data(qs.first())
    assert data == expected


def test_directory_serializer_artist(factories):
    track = factories['music.Track']()
    tf = factories['music.TrackFile'](
        track=track, bitrate=42000, duration=43, size=44)
    album = track.album
    artist = track.artist

    expected = {
        'id': artist.pk,
        'parent': 1,
        'name': artist.name,
        'child': [{
            'id': track.pk,
            'isDir': 'false',
            'title': track.title,
            'album': album.title,
            'artist': artist.name,
            'track': track.position,
            'year': track.album.release_date.year,
            'contentType': tf.mimetype,
            'suffix': tf.extension or '',
            'bitrate': 42,
            'duration': 43,
            'size': 44,
            'created': track.creation_date,
            'albumId': album.pk,
            'artistId': artist.pk,
            'parent': artist.pk,
            'type': 'music',
        }]
    }
    data = serializers.get_music_directory_data(artist)
    assert data == expected


def test_scrobble_serializer(factories):
    tf = factories['music.TrackFile']()
    track = tf.track
    user = factories['users.User']()
    payload = {
        'id': track.pk,
        'submission': True,
    }
    serializer = serializers.ScrobbleSerializer(
        data=payload, context={'user': user})

    assert serializer.is_valid(raise_exception=True)

    listening = serializer.save()

    assert listening.user == user
    assert listening.track == track
