import pytest
from rest_framework import exceptions


def test_can_insert_plt(factories):
    plt = factories["playlists.PlaylistTrack"]()
    modification_date = plt.playlist.modification_date

    assert plt.index is None

    plt.playlist.insert(plt)
    plt.refresh_from_db()

    assert plt.index == 0
    assert plt.playlist.modification_date > modification_date


def test_insert_use_last_idx_by_default(factories):
    playlist = factories["playlists.Playlist"]()
    plts = factories["playlists.PlaylistTrack"].create_batch(size=3, playlist=playlist)

    for i, plt in enumerate(plts):
        index = playlist.insert(plt)
        plt.refresh_from_db()

        assert index == i
        assert plt.index == i


def test_can_insert_at_index(factories):
    playlist = factories["playlists.Playlist"]()
    first = factories["playlists.PlaylistTrack"](playlist=playlist)
    playlist.insert(first)
    new_first = factories["playlists.PlaylistTrack"](playlist=playlist)
    index = playlist.insert(new_first, index=0)
    first.refresh_from_db()
    new_first.refresh_from_db()

    assert index == 0
    assert first.index == 1
    assert new_first.index == 0


def test_can_insert_and_move(factories):
    playlist = factories["playlists.Playlist"]()
    first = factories["playlists.PlaylistTrack"](playlist=playlist, index=0)
    second = factories["playlists.PlaylistTrack"](playlist=playlist, index=1)
    third = factories["playlists.PlaylistTrack"](playlist=playlist, index=2)

    playlist.insert(second, index=0)

    first.refresh_from_db()
    second.refresh_from_db()
    third.refresh_from_db()

    assert third.index == 2
    assert second.index == 0
    assert first.index == 1


def test_can_insert_and_move_last_to_0(factories):
    playlist = factories["playlists.Playlist"]()
    first = factories["playlists.PlaylistTrack"](playlist=playlist, index=0)
    second = factories["playlists.PlaylistTrack"](playlist=playlist, index=1)
    third = factories["playlists.PlaylistTrack"](playlist=playlist, index=2)

    playlist.insert(third, index=0)

    first.refresh_from_db()
    second.refresh_from_db()
    third.refresh_from_db()

    assert third.index == 0
    assert first.index == 1
    assert second.index == 2


def test_cannot_insert_at_wrong_index(factories):
    plt = factories["playlists.PlaylistTrack"]()
    new = factories["playlists.PlaylistTrack"](playlist=plt.playlist)
    with pytest.raises(exceptions.ValidationError):
        plt.playlist.insert(new, 2)


def test_cannot_insert_at_negative_index(factories):
    plt = factories["playlists.PlaylistTrack"]()
    new = factories["playlists.PlaylistTrack"](playlist=plt.playlist)
    with pytest.raises(exceptions.ValidationError):
        plt.playlist.insert(new, -1)


def test_remove_update_indexes(factories):
    playlist = factories["playlists.Playlist"]()
    first = factories["playlists.PlaylistTrack"](playlist=playlist, index=0)
    second = factories["playlists.PlaylistTrack"](playlist=playlist, index=1)
    third = factories["playlists.PlaylistTrack"](playlist=playlist, index=2)

    second.delete(update_indexes=True)

    first.refresh_from_db()
    third.refresh_from_db()

    assert first.index == 0
    assert third.index == 1


def test_can_insert_many(factories):
    playlist = factories["playlists.Playlist"]()
    factories["playlists.PlaylistTrack"](playlist=playlist, index=0)
    tracks = factories["music.Track"].create_batch(size=3)
    plts = playlist.insert_many(tracks)
    for i, plt in enumerate(plts):
        assert plt.index == i + 1
        assert plt.track == tracks[i]
        assert plt.playlist == playlist


def test_insert_many_honor_max_tracks(preferences, factories):
    preferences["playlists__max_tracks"] = 4
    playlist = factories["playlists.Playlist"]()
    factories["playlists.PlaylistTrack"].create_batch(size=2, playlist=playlist)
    track = factories["music.Track"]()
    with pytest.raises(exceptions.ValidationError):
        playlist.insert_many([track, track, track])


def test_can_insert_duplicate_by_default(factories):
    playlist = factories["playlists.Playlist"]()
    track = factories["music.Track"]()
    factories["playlists.PlaylistTrack"](playlist=playlist, index=0, track=track)

    new = factories["playlists.PlaylistTrack"](playlist=playlist, index=1, track=track)
    playlist.insert(new)

    new.refresh_from_db()
    assert new.index == 1


def test_cannot_insert_duplicate(factories):
    playlist = factories["playlists.Playlist"](name="playlist")
    track = factories["music.Track"]()

    factories["playlists.PlaylistTrack"](playlist=playlist, index=0, track=track)

    with pytest.raises(exceptions.ValidationError) as e:
        new = factories["playlists.PlaylistTrack"](
            playlist=playlist, index=1, track=track
        )
        playlist.insert(new, allow_duplicates=False)

    errors = e.value.detail["non_field_errors"]
    assert len(errors) == 1

    err = errors[0]
    assert err["code"] == "tracks_already_exist_in_playlist"
    assert err["playlist_name"] == "playlist"
    assert err["tracks"] == [track.title]


def test_can_insert_track_to_playlist_with_existing_duplicates(factories):
    playlist = factories["playlists.Playlist"]()
    existing_duplicate = factories["music.Track"]()
    factories["playlists.PlaylistTrack"](
        playlist=playlist, index=0, track=existing_duplicate
    )
    factories["playlists.PlaylistTrack"](
        playlist=playlist, index=1, track=existing_duplicate
    )
    factories["playlists.PlaylistTrack"](
        playlist=playlist, index=2, track=existing_duplicate
    )

    new_track = factories["music.Track"]()
    new_plt = factories["playlists.PlaylistTrack"](
        playlist=playlist, index=3, track=new_track
    )

    # no error
    playlist.insert(new_plt, allow_duplicates=False)


def test_can_insert_duplicate_with_override(factories):
    playlist = factories["playlists.Playlist"]()
    track = factories["music.Track"]()
    factories["playlists.PlaylistTrack"](playlist=playlist, index=0, track=track)

    new = factories["playlists.PlaylistTrack"](playlist=playlist, index=1, track=track)
    playlist.insert(new, allow_duplicates=True)

    new.refresh_from_db()
    assert new.index == 1


def test_can_insert_many_duplicates_by_default(factories):
    playlist = factories["playlists.Playlist"]()

    t1 = factories["music.Track"]()
    factories["playlists.PlaylistTrack"](playlist=playlist, index=0, track=t1)

    t2 = factories["music.Track"]()
    factories["playlists.PlaylistTrack"](playlist=playlist, index=1, track=t2)

    t4 = factories["music.Track"]()

    tracks = [t1, t4, t2]

    plts = playlist.insert_many(tracks)

    assert len(plts) == 3
    assert plts[0].track == t1
    assert plts[1].track == t4
    assert plts[2].track == t2


def test_cannot_insert_many_duplicates(factories):
    playlist = factories["playlists.Playlist"](name="playlist")

    t1 = factories["music.Track"]()
    factories["playlists.PlaylistTrack"](playlist=playlist, index=0, track=t1)

    t2 = factories["music.Track"]()
    factories["playlists.PlaylistTrack"](playlist=playlist, index=1, track=t2)

    t4 = factories["music.Track"]()

    with pytest.raises(exceptions.ValidationError) as e:
        tracks = [t1, t4, t2]
        playlist.insert_many(tracks, allow_duplicates=False)

    errors = e.value.detail["non_field_errors"]
    assert len(errors) == 1

    err = errors[0]
    assert err["code"] == "tracks_already_exist_in_playlist"
    assert err["playlist_name"] == "playlist"
    assert err["tracks"] == [t1.title, t2.title]


def test_can_insert_many_duplicates_with_override(factories):
    playlist = factories["playlists.Playlist"]()

    t1 = factories["music.Track"]()
    factories["playlists.PlaylistTrack"](playlist=playlist, index=0, track=t1)

    t2 = factories["music.Track"]()
    factories["playlists.PlaylistTrack"](playlist=playlist, index=1, track=t2)

    t4 = factories["music.Track"]()

    tracks = [t1, t4, t2]

    plts = playlist.insert_many(tracks, allow_duplicates=True)

    assert len(plts) == 3
    assert plts[0].track == t1
    assert plts[1].track == t4
    assert plts[2].track == t2


@pytest.mark.parametrize(
    "privacy_level,expected", [("me", False), ("instance", False), ("everyone", True)]
)
def test_playlist_track_playable_by_anonymous(privacy_level, expected, factories):
    plt = factories["playlists.PlaylistTrack"]()
    track = plt.track
    factories["music.Upload"](
        track=track, library__privacy_level=privacy_level, import_status="finished"
    )
    queryset = plt.__class__.objects.playable_by(None).annotate_playable_by_actor(None)
    match = plt in list(queryset)
    assert match is expected
    if expected:
        assert bool(queryset.first().is_playable_by_actor) is expected


@pytest.mark.parametrize(
    "privacy_level,expected", [("me", False), ("instance", False), ("everyone", True)]
)
def test_playlist_playable_by_anonymous(privacy_level, expected, factories):
    plt = factories["playlists.PlaylistTrack"]()
    playlist = plt.playlist
    track = plt.track
    factories["music.Upload"](
        track=track, library__privacy_level=privacy_level, import_status="finished"
    )
    queryset = playlist.__class__.objects.playable_by(None).with_playable_plts(None)
    match = playlist in list(queryset)
    assert match is expected
