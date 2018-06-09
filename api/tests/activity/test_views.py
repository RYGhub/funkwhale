from django.urls import reverse

from funkwhale_api.activity import serializers
from funkwhale_api.activity import utils


def test_activity_view(factories, api_client, preferences, anonymous_user):
    preferences["common__api_authentication_required"] = False
    favorite = factories["favorites.TrackFavorite"](user__privacy_level="everyone")
    factories["history.Listening"]()
    url = reverse("api:v1:activity-list")
    objects = utils.get_activity(anonymous_user)
    serializer = serializers.AutoSerializer(objects, many=True)
    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data["results"] == serializer.data
