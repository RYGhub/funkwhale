import pytest

from rest_framework import exceptions


def test_can_insert_plt(factories):
    plt = factories['playlists.PlaylistTrack']()
    modification_date = plt.playlist.modification_date

    assert plt.index is None

    plt.playlist.insert(plt)
    plt.refresh_from_db()

    assert plt.index == 0
    assert plt.playlist.modification_date > modification_date


def test_insert_use_last_idx_by_default(factories):
    playlist = factories['playlists.Playlist']()
    plts = factories['playlists.PlaylistTrack'].create_batch(
        size=3, playlist=playlist)

    for i, plt in enumerate(plts):
        index = playlist.insert(plt)
        plt.refresh_from_db()

        assert index == i
        assert plt.index == i

def test_can_insert_at_index(factories):
    playlist = factories['playlists.Playlist']()
    first = factories['playlists.PlaylistTrack'](playlist=playlist)
    playlist.insert(first)
    new_first = factories['playlists.PlaylistTrack'](playlist=playlist)
    index = playlist.insert(new_first, index=0)
    first.refresh_from_db()
    new_first.refresh_from_db()

    assert index == 0
    assert first.index == 1
    assert new_first.index == 0


def test_can_insert_and_move(factories):
    playlist = factories['playlists.Playlist']()
    first = factories['playlists.PlaylistTrack'](playlist=playlist, index=0)
    second = factories['playlists.PlaylistTrack'](playlist=playlist, index=1)
    third = factories['playlists.PlaylistTrack'](playlist=playlist, index=2)

    playlist.insert(second, index=0)

    first.refresh_from_db()
    second.refresh_from_db()
    third.refresh_from_db()

    assert third.index == 2
    assert second.index == 0
    assert first.index == 1


def test_can_insert_and_move_last_to_0(factories):
    playlist = factories['playlists.Playlist']()
    first = factories['playlists.PlaylistTrack'](playlist=playlist, index=0)
    second = factories['playlists.PlaylistTrack'](playlist=playlist, index=1)
    third = factories['playlists.PlaylistTrack'](playlist=playlist, index=2)

    playlist.insert(third, index=0)

    first.refresh_from_db()
    second.refresh_from_db()
    third.refresh_from_db()

    assert third.index == 0
    assert first.index == 1
    assert second.index == 2


def test_cannot_insert_at_wrong_index(factories):
    plt = factories['playlists.PlaylistTrack']()
    new = factories['playlists.PlaylistTrack'](playlist=plt.playlist)
    with pytest.raises(exceptions.ValidationError):
        plt.playlist.insert(new, 2)


def test_cannot_insert_at_negative_index(factories):
    plt = factories['playlists.PlaylistTrack']()
    new = factories['playlists.PlaylistTrack'](playlist=plt.playlist)
    with pytest.raises(exceptions.ValidationError):
        plt.playlist.insert(new, -1)


def test_remove_update_indexes(factories):
    playlist = factories['playlists.Playlist']()
    first = factories['playlists.PlaylistTrack'](playlist=playlist, index=0)
    second = factories['playlists.PlaylistTrack'](playlist=playlist, index=1)
    third = factories['playlists.PlaylistTrack'](playlist=playlist, index=2)

    second.delete(update_indexes=True)

    first.refresh_from_db()
    third.refresh_from_db()

    assert first.index == 0
    assert third.index == 1


def test_can_insert_many(factories):
    playlist = factories['playlists.Playlist']()
    existing = factories['playlists.PlaylistTrack'](playlist=playlist, index=0)
    tracks = factories['music.Track'].create_batch(size=3)
    plts = playlist.insert_many(tracks)
    for i, plt in enumerate(plts):
        assert plt.index == i + 1
        assert plt.track == tracks[i]
        assert plt.playlist == playlist


def test_insert_many_honor_max_tracks(preferences, factories):
    preferences['playlists__max_tracks'] = 4
    playlist = factories['playlists.Playlist']()
    plts = factories['playlists.PlaylistTrack'].create_batch(
        size=2, playlist=playlist)
    track = factories['music.Track']()
    with pytest.raises(exceptions.ValidationError):
        playlist.insert_many([track, track, track])
