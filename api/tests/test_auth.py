from django.urls import reverse
from rest_framework_jwt.settings import api_settings

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


def test_can_authenticate_using_jwt_token_param_in_url(factories, preferences, client):
    user = factories["users.User"]()
    preferences["common__api_authentication_required"] = True
    url = reverse("api:v1:tracks-list")
    response = client.get(url)

    assert response.status_code == 401

    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)
    response = client.get(url, data={"jwt": token})
    assert response.status_code == 200


def test_can_authenticate_using_oauth_token_param_in_url(
    factories, preferences, client, mocker
):
    mocker.patch(
        "funkwhale_api.users.oauth.permissions.should_allow", return_value=True
    )
    token = factories["users.AccessToken"]()
    preferences["common__api_authentication_required"] = True
    url = reverse("api:v1:tracks-list")
    response = client.get(url)

    assert response.status_code == 401

    response = client.get(url, data={"token": token.token})
    assert response.status_code == 200
