from funkwhale_api.users.serializers import UserActivitySerializer
from funkwhale_api.favorites import serializers


def test_get_favorite_activity_url(settings, factories):
    favorite = factories['favorites.TrackFavorite']()
    user_url = favorite.user.get_activity_url()
    expected = '{}/favorites/tracks/{}'.format(
        user_url, favorite.pk)
    assert favorite.get_activity_url() == expected


def test_activity_favorite_serializer(factories):
    favorite = factories['favorites.TrackFavorite']()

    actor = UserActivitySerializer(favorite.user).data
    field = serializers.serializers.DateTimeField()
    expected = {
        "type": "Like",
        "id": favorite.get_activity_url(),
        "actor": actor,
        "object": favorite.track.get_activity_url(),
        "published": field.to_representation(favorite.creation_date),
    }

    data = serializers.TrackFavoriteActivitySerializer(favorite).data

    assert data == expected
