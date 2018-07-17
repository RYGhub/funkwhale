from funkwhale_api.playlists import models, serializers


def test_cannot_max_500_tracks_per_playlist(factories, preferences):
    preferences["playlists__max_tracks"] = 2
    playlist = factories["playlists.Playlist"]()
    factories["playlists.PlaylistTrack"].create_batch(size=2, playlist=playlist)
    track = factories["music.Track"]()
    serializer = serializers.PlaylistTrackWriteSerializer(
        data={"playlist": playlist.pk, "track": track.pk}
    )

    assert serializer.is_valid() is False
    assert "playlist" in serializer.errors


def test_create_insert_is_called_when_index_is_None(factories, mocker):
    insert = mocker.spy(models.Playlist, "insert")
    playlist = factories["playlists.Playlist"]()
    track = factories["music.Track"]()
    serializer = serializers.PlaylistTrackWriteSerializer(
        data={"playlist": playlist.pk, "track": track.pk, "index": None}
    )
    assert serializer.is_valid() is True

    plt = serializer.save()
    insert.assert_called_once_with(playlist, plt, None)
    assert plt.index == 0


def test_create_insert_is_called_when_index_is_provided(factories, mocker):
    playlist = factories["playlists.Playlist"]()
    first = factories["playlists.PlaylistTrack"](playlist=playlist, index=0)
    insert = mocker.spy(models.Playlist, "insert")
    factories["playlists.Playlist"]()
    track = factories["music.Track"]()
    serializer = serializers.PlaylistTrackWriteSerializer(
        data={"playlist": playlist.pk, "track": track.pk, "index": 0}
    )
    assert serializer.is_valid() is True

    plt = serializer.save()
    first.refresh_from_db()
    insert.assert_called_once_with(playlist, plt, 0)
    assert plt.index == 0
    assert first.index == 1


def test_update_insert_is_called_when_index_is_provided(factories, mocker):
    playlist = factories["playlists.Playlist"]()
    first = factories["playlists.PlaylistTrack"](playlist=playlist, index=0)
    second = factories["playlists.PlaylistTrack"](playlist=playlist, index=1)
    insert = mocker.spy(models.Playlist, "insert")
    factories["playlists.Playlist"]()
    factories["music.Track"]()
    serializer = serializers.PlaylistTrackWriteSerializer(
        second, data={"playlist": playlist.pk, "track": second.track.pk, "index": 0}
    )
    assert serializer.is_valid() is True

    plt = serializer.save()
    first.refresh_from_db()
    insert.assert_called_once_with(playlist, plt, 0)
    assert plt.index == 0
    assert first.index == 1


def test_playlist_serializer_include_covers(factories, api_request):
    playlist = factories["playlists.Playlist"]()
    t1 = factories["music.Track"]()
    t2 = factories["music.Track"]()
    t3 = factories["music.Track"](album__cover=None)
    t4 = factories["music.Track"]()
    t5 = factories["music.Track"]()
    t6 = factories["music.Track"]()
    t7 = factories["music.Track"]()

    playlist.insert_many([t1, t2, t3, t4, t5, t6, t7])
    request = api_request.get("/")
    qs = playlist.__class__.objects.with_covers().with_tracks_count()

    expected = [
        request.build_absolute_uri(t1.album.cover.url),
        request.build_absolute_uri(t2.album.cover.url),
        request.build_absolute_uri(t4.album.cover.url),
        request.build_absolute_uri(t5.album.cover.url),
        request.build_absolute_uri(t6.album.cover.url),
    ]

    serializer = serializers.PlaylistSerializer(qs.get(), context={"request": request})
    assert serializer.data["album_covers"] == expected


def test_playlist_serializer_include_duration(factories, api_request):
    playlist = factories["playlists.Playlist"]()
    tf1 = factories["music.TrackFile"](duration=15)
    tf2 = factories["music.TrackFile"](duration=30)
    playlist.insert_many([tf1.track, tf2.track])
    qs = playlist.__class__.objects.with_duration().with_tracks_count()

    serializer = serializers.PlaylistSerializer(qs.get())
    assert serializer.data["duration"] == 45
