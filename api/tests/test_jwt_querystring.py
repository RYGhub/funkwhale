from django.urls import reverse
from rest_framework_jwt.settings import api_settings

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


def test_can_authenticate_using_token_param_in_url(factories, settings, client):
    user = factories['users.User']()
    settings.API_AUTHENTICATION_REQUIRED = True
    url = reverse('api:v1:tracks-list')
    response = client.get(url)

    assert response.status_code == 401

    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)
    response = client.get(url, data={
        'jwt': token
    })
    assert response.status_code == 200
