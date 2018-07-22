import pytest

from django.urls import reverse


@pytest.mark.parametrize("level", ["instance", "me", "followers"])
def test_privacy_filter(preferences, level, factories, api_client):
    preferences["common__api_authentication_required"] = False
    factories["history.Listening"](user__privacy_level=level)
    url = reverse("api:v1:history:listenings-list")
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data["count"] == 0
