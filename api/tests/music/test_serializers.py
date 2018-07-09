from funkwhale_api.music import serializers


def test_artist_album_serializer(factories, to_api_date):
    track = factories["music.Track"]()
    album = track.album
    album = album.__class__.objects.with_tracks_count().get(pk=album.pk)
    expected = {
        "id": album.id,
        "mbid": str(album.mbid),
        "title": album.title,
        "artist": album.artist.id,
        "creation_date": to_api_date(album.creation_date),
        "tracks_count": 1,
        "cover": album.cover.url,
        "release_date": to_api_date(album.release_date),
    }
    serializer = serializers.ArtistAlbumSerializer(album)

    assert serializer.data == expected


def test_artist_with_albums_serializer(factories, to_api_date):
    track = factories["music.Track"]()
    artist = track.artist
    artist = artist.__class__.objects.with_albums().get(pk=artist.pk)
    album = list(artist.albums.all())[0]

    expected = {
        "id": artist.id,
        "mbid": str(artist.mbid),
        "name": artist.name,
        "creation_date": to_api_date(artist.creation_date),
        "albums": [serializers.ArtistAlbumSerializer(album).data],
    }
    serializer = serializers.ArtistWithAlbumsSerializer(artist)
    assert serializer.data == expected


def test_album_track_serializer(factories, to_api_date):
    tf = factories["music.TrackFile"]()
    track = tf.track

    expected = {
        "id": track.id,
        "artist": serializers.ArtistSimpleSerializer(track.artist).data,
        "album": track.album.id,
        "mbid": str(track.mbid),
        "title": track.title,
        "position": track.position,
        "creation_date": to_api_date(track.creation_date),
        "files": [serializers.TrackFileSerializer(tf).data],
    }
    serializer = serializers.AlbumTrackSerializer(track)
    assert serializer.data == expected


def test_track_file_serializer(factories, to_api_date):
    tf = factories["music.TrackFile"]()

    expected = {
        "id": tf.id,
        "path": tf.path,
        "source": tf.source,
        "filename": tf.filename,
        "track": tf.track.pk,
        "duration": tf.duration,
        "mimetype": tf.mimetype,
        "bitrate": tf.bitrate,
        "size": tf.size,
    }
    serializer = serializers.TrackFileSerializer(tf)
    assert serializer.data == expected


def test_album_serializer(factories, to_api_date):
    track1 = factories["music.Track"](position=2)
    track2 = factories["music.Track"](position=1, album=track1.album)
    album = track1.album
    expected = {
        "id": album.id,
        "mbid": str(album.mbid),
        "title": album.title,
        "artist": serializers.ArtistSimpleSerializer(album.artist).data,
        "creation_date": to_api_date(album.creation_date),
        "cover": album.cover.url,
        "release_date": to_api_date(album.release_date),
        "tracks": serializers.AlbumTrackSerializer([track2, track1], many=True).data,
    }
    serializer = serializers.AlbumSerializer(album)

    assert serializer.data == expected


def test_track_serializer(factories, to_api_date):
    tf = factories["music.TrackFile"]()
    track = tf.track

    expected = {
        "id": track.id,
        "artist": serializers.ArtistSimpleSerializer(track.artist).data,
        "album": serializers.TrackAlbumSerializer(track.album).data,
        "mbid": str(track.mbid),
        "title": track.title,
        "position": track.position,
        "creation_date": to_api_date(track.creation_date),
        "lyrics": track.get_lyrics_url(),
        "files": [serializers.TrackFileSerializer(tf).data],
    }
    serializer = serializers.TrackSerializer(track)
    assert serializer.data == expected
