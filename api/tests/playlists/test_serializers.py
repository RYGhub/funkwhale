from funkwhale_api.playlists import models, serializers


def test_cannot_max_500_tracks_per_playlist(factories, preferences):
    preferences["playlists__max_tracks"] = 2
    playlist = factories["playlists.Playlist"]()
    plts = factories["playlists.PlaylistTrack"].create_batch(size=2, playlist=playlist)
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
