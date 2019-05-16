from funkwhale_api.music import filters
from funkwhale_api.music import models


def test_album_filter_hidden(factories, mocker, queryset_equal_list):
    factories["music.Album"]()
    cf = factories["moderation.UserFilter"](for_artist=True)
    hidden_album = factories["music.Album"](artist=cf.target_artist)

    qs = models.Album.objects.all()
    filterset = filters.AlbumFilter(
        {"hidden": "true"}, request=mocker.Mock(user=cf.user), queryset=qs
    )

    assert filterset.qs == [hidden_album]


def test_artist_filter_hidden(factories, mocker, queryset_equal_list):
    factories["music.Artist"]()
    cf = factories["moderation.UserFilter"](for_artist=True)
    hidden_artist = cf.target_artist

    qs = models.Artist.objects.all()
    filterset = filters.ArtistFilter(
        {"hidden": "true"}, request=mocker.Mock(user=cf.user), queryset=qs
    )

    assert filterset.qs == [hidden_artist]


def test_artist_filter_track_artist(factories, mocker, queryset_equal_list):
    factories["music.Track"]()
    cf = factories["moderation.UserFilter"](for_artist=True)
    hidden_track = factories["music.Track"](artist=cf.target_artist)

    qs = models.Track.objects.all()
    filterset = filters.TrackFilter(
        {"hidden": "true"}, request=mocker.Mock(user=cf.user), queryset=qs
    )

    assert filterset.qs == [hidden_track]


def test_artist_filter_track_album_artist(factories, mocker, queryset_equal_list):
    factories["music.Track"]()
    cf = factories["moderation.UserFilter"](for_artist=True)
    hidden_track = factories["music.Track"](album__artist=cf.target_artist)

    qs = models.Track.objects.all()
    filterset = filters.TrackFilter(
        {"hidden": "true"}, request=mocker.Mock(user=cf.user), queryset=qs
    )

    assert filterset.qs == [hidden_track]
