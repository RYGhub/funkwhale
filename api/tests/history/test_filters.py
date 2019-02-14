from funkwhale_api.history import filters
from funkwhale_api.history import models


def test_listening_filter_track_artist(factories, mocker, queryset_equal_list):
    factories["history.Listening"]()
    cf = factories["moderation.UserFilter"](for_artist=True)
    hidden_listening = factories["history.Listening"](track__artist=cf.target_artist)
    qs = models.Listening.objects.all()
    filterset = filters.ListeningFilter(
        {"hidden": "true"}, request=mocker.Mock(user=cf.user), queryset=qs
    )

    assert filterset.qs == [hidden_listening]


def test_listening_filter_track_album_artist(factories, mocker, queryset_equal_list):
    factories["history.Listening"]()
    cf = factories["moderation.UserFilter"](for_artist=True)
    hidden_listening = factories["history.Listening"](
        track__album__artist=cf.target_artist
    )
    qs = models.Listening.objects.all()
    filterset = filters.ListeningFilter(
        {"hidden": "true"}, request=mocker.Mock(user=cf.user), queryset=qs
    )

    assert filterset.qs == [hidden_listening]
