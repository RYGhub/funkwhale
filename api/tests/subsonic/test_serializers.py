import datetime
import pytest

from funkwhale_api.music import models as music_models
from funkwhale_api.subsonic import serializers


@pytest.mark.parametrize(
    "date, expected",
    [
        (datetime.datetime(2017, 1, 12, 9, 53, 12, 1890), "2017-01-12T09:53:12.000Z"),
        (None, None),
    ],
)
def test_to_subsonic_date(date, expected):
    assert serializers.to_subsonic_date(date) == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        ("AC/DC", "AC_DC"),
        ("AC-DC", "AC-DC"),
        ("A" * 100, "A" * 50),
        ("Album (2019)", "Album (2019)"),
        ("Haven't", "Haven_t"),
    ],
)
def test_get_valid_filepart(input, expected):
    assert serializers.get_valid_filepart(input) == expected


@pytest.mark.parametrize(
    "factory_kwargs, suffix, expected",
    [
        (
            {
                "artist__name": "Hello",
                "album__title": "World",
                "title": "foo",
                "position": None,
            },
            "mp3",
            "Hello/World/foo.mp3",
        ),
        (
            {
                "artist__name": "AC/DC",
                "album__title": "escape/my",
                "title": "sla/sh",
                "position": 12,
            },
            "ogg",
            "/".join(
                [
                    serializers.get_valid_filepart("AC/DC"),
                    serializers.get_valid_filepart("escape/my"),
                ]
            )
            + "/12 - {}.ogg".format(serializers.get_valid_filepart("sla/sh")),
        ),
    ],
)
def test_get_track_path(factory_kwargs, suffix, expected, factories):
    track = factories["music.Track"](**factory_kwargs)
    assert serializers.get_track_path(track, suffix) == expected


def test_get_artists_serializer(factories):
    artist1 = factories["music.Artist"](name="eliot")
    artist2 = factories["music.Artist"](name="Ellena")
    artist3 = factories["music.Artist"](name="Rilay")
    artist4 = factories["music.Artist"](name="")  # Shouldn't be serialised

    factories["music.Album"].create_batch(size=3, artist=artist1)
    factories["music.Album"].create_batch(size=2, artist=artist2)

    expected = {
        "ignoredArticles": "",
        "index": [
            {
                "name": "E",
                "artist": [
                    {"id": artist1.pk, "name": artist1.name, "albumCount": 3},
                    {"id": artist2.pk, "name": artist2.name, "albumCount": 2},
                ],
            },
            {
                "name": "R",
                "artist": [{"id": artist3.pk, "name": artist3.name, "albumCount": 0}],
            },
        ],
    }

    queryset = artist1.__class__.objects.filter(
        pk__in=[artist1.pk, artist2.pk, artist3.pk, artist4.pk]
    )

    assert serializers.GetArtistsSerializer(queryset).data == expected


def test_get_artist_serializer(factories):
    artist = factories["music.Artist"]()
    album = factories["music.Album"](artist=artist)
    tracks = factories["music.Track"].create_batch(size=3, album=album)

    expected = {
        "id": artist.pk,
        "name": artist.name,
        "albumCount": 1,
        "album": [
            {
                "id": album.pk,
                "coverArt": "al-{}".format(album.id),
                "artistId": artist.pk,
                "name": album.title,
                "artist": artist.name,
                "songCount": len(tracks),
                "created": serializers.to_subsonic_date(album.creation_date),
                "year": album.release_date.year,
            }
        ],
    }

    assert serializers.GetArtistSerializer(artist).data == expected


@pytest.mark.parametrize(
    "mimetype, extension, expected",
    [
        ("audio/ogg", "noop", "audio/ogg"),
        ("", "ogg", "audio/ogg"),
        ("", "mp3", "audio/mpeg"),
        ("", "", "audio/mpeg"),
    ],
)
def test_get_track_data_content_type(mimetype, extension, expected, factories):
    upload = factories["music.Upload"]()
    upload.mimetype = mimetype
    upload.audio_file = "test.{}".format(extension)

    data = serializers.get_track_data(
        album=upload.track.album, track=upload.track, upload=upload
    )

    assert data["contentType"] == expected


def test_get_album_serializer(factories):
    artist = factories["music.Artist"]()
    album = factories["music.Album"](artist=artist)
    track = factories["music.Track"](album=album, disc_number=42)
    upload = factories["music.Upload"](track=track, bitrate=42000, duration=43, size=44)

    expected = {
        "id": album.pk,
        "artistId": artist.pk,
        "name": album.title,
        "artist": artist.name,
        "songCount": 1,
        "created": serializers.to_subsonic_date(album.creation_date),
        "year": album.release_date.year,
        "coverArt": "al-{}".format(album.id),
        "song": [
            {
                "id": track.pk,
                "isDir": "false",
                "title": track.title,
                "coverArt": "al-{}".format(album.id),
                "album": album.title,
                "artist": artist.name,
                "track": track.position,
                "discNumber": track.disc_number,
                "year": track.album.release_date.year,
                "contentType": upload.mimetype,
                "suffix": upload.extension or "",
                "path": serializers.get_track_path(track, upload.extension),
                "bitrate": 42,
                "duration": 43,
                "size": 44,
                "created": serializers.to_subsonic_date(track.creation_date),
                "albumId": album.pk,
                "artistId": artist.pk,
                "type": "music",
            }
        ],
    }

    assert serializers.GetAlbumSerializer(album).data == expected


def test_starred_tracks2_serializer(factories):
    artist = factories["music.Artist"]()
    album = factories["music.Album"](artist=artist)
    track = factories["music.Track"](album=album)
    upload = factories["music.Upload"](track=track)
    favorite = factories["favorites.TrackFavorite"](track=track)
    expected = [serializers.get_track_data(album, track, upload)]
    expected[0]["starred"] = serializers.to_subsonic_date(favorite.creation_date)
    data = serializers.get_starred_tracks_data([favorite])
    assert data == expected


def test_get_album_list2_serializer(factories):
    album1 = factories["music.Album"]()
    album2 = factories["music.Album"]()

    qs = music_models.Album.objects.with_tracks_count().order_by("pk")
    expected = [
        serializers.get_album2_data(album1),
        serializers.get_album2_data(album2),
    ]
    data = serializers.get_album_list2_data(qs)
    assert data == expected


def test_playlist_serializer(factories):
    plt = factories["playlists.PlaylistTrack"]()
    playlist = plt.playlist
    qs = music_models.Album.objects.with_tracks_count().order_by("pk")
    expected = {
        "id": playlist.pk,
        "name": playlist.name,
        "owner": playlist.user.username,
        "public": "false",
        "songCount": 1,
        "duration": 0,
        "created": serializers.to_subsonic_date(playlist.creation_date),
    }
    qs = playlist.__class__.objects.with_tracks_count()
    data = serializers.get_playlist_data(qs.first())
    assert data == expected


def test_playlist_detail_serializer(factories):
    plt = factories["playlists.PlaylistTrack"]()
    upload = factories["music.Upload"](track=plt.track)
    playlist = plt.playlist
    qs = music_models.Album.objects.with_tracks_count().order_by("pk")
    expected = {
        "id": playlist.pk,
        "name": playlist.name,
        "owner": playlist.user.username,
        "public": "false",
        "songCount": 1,
        "duration": 0,
        "created": serializers.to_subsonic_date(playlist.creation_date),
        "entry": [serializers.get_track_data(plt.track.album, plt.track, upload)],
    }
    qs = playlist.__class__.objects.with_tracks_count()
    data = serializers.get_playlist_detail_data(qs.first())
    assert data == expected


def test_directory_serializer_artist(factories):
    track = factories["music.Track"]()
    upload = factories["music.Upload"](track=track, bitrate=42000, duration=43, size=44)
    album = track.album
    artist = track.artist

    expected = {
        "id": artist.pk,
        "parent": 1,
        "name": artist.name,
        "child": [
            {
                "id": track.pk,
                "isDir": "false",
                "title": track.title,
                "album": album.title,
                "artist": artist.name,
                "track": track.position,
                "year": track.album.release_date.year,
                "contentType": upload.mimetype,
                "suffix": upload.extension or "",
                "path": serializers.get_track_path(track, upload.extension),
                "bitrate": 42,
                "duration": 43,
                "size": 44,
                "created": serializers.to_subsonic_date(track.creation_date),
                "albumId": album.pk,
                "artistId": artist.pk,
                "parent": artist.pk,
                "type": "music",
            }
        ],
    }
    data = serializers.get_music_directory_data(artist)
    assert data == expected


def test_scrobble_serializer(factories):
    upload = factories["music.Upload"]()
    track = upload.track
    user = factories["users.User"]()
    payload = {"id": track.pk, "submission": True}
    serializer = serializers.ScrobbleSerializer(data=payload, context={"user": user})

    assert serializer.is_valid(raise_exception=True)

    listening = serializer.save()

    assert listening.user == user
    assert listening.track == track


def test_channel_serializer(factories):
    description = factories["common.Content"]()
    channel = factories["audio.Channel"](external=True, artist__description=description)
    upload = factories["music.Upload"](
        playable=True, library=channel.library, duration=42
    )

    expected = {
        "id": str(channel.uuid),
        "url": channel.rss_url,
        "title": channel.artist.name,
        "description": description.as_plain_text,
        "coverArt": "at-{}".format(channel.artist.attachment_cover.uuid),
        "originalImageUrl": channel.artist.attachment_cover.url,
        "status": "completed",
        "episode": [serializers.get_channel_episode_data(upload, channel.uuid)],
    }
    data = serializers.get_channel_data(channel, [upload])
    assert data == expected


def test_channel_episode_serializer(factories):
    description = factories["common.Content"]()
    channel = factories["audio.Channel"]()
    track = factories["music.Track"](description=description, artist=channel.artist)
    upload = factories["music.Upload"](
        playable=True, track=track, bitrate=128000, duration=42
    )

    expected = {
        "id": str(upload.uuid),
        "channelId": str(channel.uuid),
        "streamId": upload.track.id,
        "title": track.title,
        "description": description.as_plain_text,
        "coverArt": "at-{}".format(track.attachment_cover.uuid),
        "isDir": "false",
        "year": track.creation_date.year,
        "created": track.creation_date.isoformat(),
        "publishDate": track.creation_date.isoformat(),
        "genre": "Podcast",
        "size": upload.size,
        "duration": upload.duration,
        "bitrate": upload.bitrate / 1000,
        "contentType": upload.mimetype,
        "suffix": upload.extension,
        "status": "completed",
    }
    data = serializers.get_channel_episode_data(upload, channel.uuid)
    assert data == expected
