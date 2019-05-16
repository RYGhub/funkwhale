from funkwhale_api.moderation import filters
from funkwhale_api.music import models as music_models


def test_hidden_defaults_to_true(factories, queryset_equal_list, mocker):
    user = factories["users.User"]()
    artist = factories["music.Artist"]()
    hidden_artist = factories["music.Artist"]()
    factories["moderation.UserFilter"](target_artist=hidden_artist, user=user)

    class FS(filters.HiddenContentFilterSet):
        class Meta:
            hidden_content_fields_mapping = {"target_artist": ["pk"]}

    filterset = FS(
        data={},
        queryset=music_models.Artist.objects.all(),
        request=mocker.Mock(user=user),
    )
    assert filterset.data["hidden"] is False
    queryset = filterset.filter_hidden_content(
        music_models.Artist.objects.all(), "", False
    )

    assert queryset == [artist]


def test_hidden_false(factories, queryset_equal_list, mocker):
    user = factories["users.User"]()
    factories["music.Artist"]()
    hidden_artist = factories["music.Artist"]()
    factories["moderation.UserFilter"](target_artist=hidden_artist, user=user)

    class FS(filters.HiddenContentFilterSet):
        class Meta:
            hidden_content_fields_mapping = {"target_artist": ["pk"]}

    filterset = FS(
        data={},
        queryset=music_models.Artist.objects.all(),
        request=mocker.Mock(user=user),
    )

    queryset = filterset.filter_hidden_content(
        music_models.Artist.objects.all(), "", True
    )

    assert queryset == [hidden_artist]


def test_hidden_anonymous(factories, queryset_equal_list, mocker, anonymous_user):
    artist = factories["music.Artist"]()

    class FS(filters.HiddenContentFilterSet):
        class Meta:
            hidden_content_fields_mapping = {"target_artist": ["pk"]}

    filterset = FS(
        data={},
        queryset=music_models.Artist.objects.all(),
        request=mocker.Mock(user=anonymous_user),
    )

    queryset = filterset.filter_hidden_content(
        music_models.Artist.objects.all(), "", True
    )

    assert queryset == [artist]
