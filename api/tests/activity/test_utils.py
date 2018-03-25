from funkwhale_api.activity import utils


def test_get_activity(factories):
    user = factories['users.User']()
    listening = factories['history.Listening']()
    favorite = factories['favorites.TrackFavorite']()

    objects = list(utils.get_activity(user))
    assert objects == [favorite, listening]


def test_get_activity_honors_privacy_level(factories, anonymous_user):
    listening = factories['history.Listening'](user__privacy_level='me')
    favorite1 = factories['favorites.TrackFavorite'](
        user__privacy_level='everyone')
    favorite2 = factories['favorites.TrackFavorite'](
        user__privacy_level='instance')

    objects = list(utils.get_activity(anonymous_user))
    assert objects == [favorite1]
