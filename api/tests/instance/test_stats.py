from funkwhale_api.instance import stats


def test_get_users(mocker):
    mocker.patch("funkwhale_api.users.models.User.objects.count", return_value=42)

    assert stats.get_users() == 42


def test_get_music_duration(factories):
    factories["music.TrackFile"].create_batch(size=5, duration=360)

    # duration is in hours
    assert stats.get_music_duration() == 0.5


def test_get_listenings(mocker):
    mocker.patch(
        "funkwhale_api.history.models.Listening.objects.count", return_value=42
    )
    assert stats.get_listenings() == 42


def test_get_track_favorites(mocker):
    mocker.patch(
        "funkwhale_api.favorites.models.TrackFavorite.objects.count", return_value=42
    )
    assert stats.get_track_favorites() == 42


def test_get_tracks(mocker):
    mocker.patch("funkwhale_api.music.models.Track.objects.count", return_value=42)
    assert stats.get_tracks() == 42


def test_get_albums(mocker):
    mocker.patch("funkwhale_api.music.models.Album.objects.count", return_value=42)
    assert stats.get_albums() == 42


def test_get_artists(mocker):
    mocker.patch("funkwhale_api.music.models.Artist.objects.count", return_value=42)
    assert stats.get_artists() == 42


def test_get(mocker):
    keys = [
        "users",
        "tracks",
        "albums",
        "artists",
        "track_favorites",
        "listenings",
        "music_duration",
    ]
    [
        mocker.patch.object(stats, "get_{}".format(k), return_value=i)
        for i, k in enumerate(keys)
    ]

    expected = {k: i for i, k in enumerate(keys)}

    assert stats.get() == expected
