from funkwhale_api.federation import serializers as federation_serializers
from funkwhale_api.favorites import serializers
from funkwhale_api.music import serializers as music_serializers
from funkwhale_api.users import serializers as users_serializers


def test_track_favorite_serializer(factories, to_api_date):
    favorite = factories["favorites.TrackFavorite"]()
    actor = favorite.user.create_actor()

    expected = {
        "id": favorite.pk,
        "creation_date": to_api_date(favorite.creation_date),
        "track": music_serializers.TrackSerializer(favorite.track).data,
        "actor": federation_serializers.APIActorSerializer(actor).data,
        "user": users_serializers.UserBasicSerializer(favorite.user).data,
    }
    serializer = serializers.UserTrackFavoriteSerializer(favorite)

    assert serializer.data == expected
