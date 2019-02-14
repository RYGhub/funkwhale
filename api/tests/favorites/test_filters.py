from funkwhale_api.favorites import filters
from funkwhale_api.favorites import models


def test_track_favorite_filter_track_artist(factories, mocker, queryset_equal_list):
    factories["favorites.TrackFavorite"]()
    cf = factories["moderation.UserFilter"](for_artist=True)
    hidden_fav = factories["favorites.TrackFavorite"](track__artist=cf.target_artist)
    qs = models.TrackFavorite.objects.all()
    filterset = filters.TrackFavoriteFilter(
        {"hidden": "true"}, request=mocker.Mock(user=cf.user), queryset=qs
    )

    assert filterset.qs == [hidden_fav]


def test_track_favorite_filter_track_album_artist(
    factories, mocker, queryset_equal_list
):
    factories["favorites.TrackFavorite"]()
    cf = factories["moderation.UserFilter"](for_artist=True)
    hidden_fav = factories["favorites.TrackFavorite"](
        track__album__artist=cf.target_artist
    )
    qs = models.TrackFavorite.objects.all()
    filterset = filters.TrackFavoriteFilter(
        {"hidden": "true"}, request=mocker.Mock(user=cf.user), queryset=qs
    )

    assert filterset.qs == [hidden_fav]
