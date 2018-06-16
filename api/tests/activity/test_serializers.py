from funkwhale_api.activity import serializers
from funkwhale_api.favorites.serializers import TrackFavoriteActivitySerializer
from funkwhale_api.history.serializers import ListeningActivitySerializer


def test_autoserializer(factories):
    favorite = factories["favorites.TrackFavorite"]()
    listening = factories["history.Listening"]()
    objects = [favorite, listening]
    serializer = serializers.AutoSerializer(objects, many=True)
    expected = [
        TrackFavoriteActivitySerializer(favorite).data,
        ListeningActivitySerializer(listening).data,
    ]

    assert serializer.data == expected
