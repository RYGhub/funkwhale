from django.urls import reverse

from funkwhale_api.activity import serializers
from funkwhale_api.activity import utils


def test_activity_view(factories, api_client, settings, anonymous_user):
    settings.API_AUTHENTICATION_REQUIRED = False
    favorite = factories['favorites.TrackFavorite'](
        user__privacy_level='everyone')
    listening = factories['history.Listening']()
    url = reverse('api:v1:activity-list')
    objects = utils.get_activity(anonymous_user)
    serializer = serializers.AutoSerializer(objects, many=True)
    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data['results'] == serializer.data
