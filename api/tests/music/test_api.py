import os

import pytest
from django.urls import reverse


DATA_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.parametrize(
    "route,method",
    [
        ("api:v1:tags-list", "get"),
        ("api:v1:tracks-list", "get"),
        ("api:v1:artists-list", "get"),
        ("api:v1:albums-list", "get"),
    ],
)
def test_can_restrict_api_views_to_authenticated_users(
    db, route, method, preferences, client
):
    url = reverse(route)
    preferences["common__api_authentication_required"] = True
    response = getattr(client, method)(url)
    assert response.status_code == 401


def test_upload_url_is_restricted_to_authenticated_users(
    api_client, factories, preferences
):
    preferences["common__api_authentication_required"] = True
    upload = factories["music.Upload"](library__privacy_level="instance")
    assert upload.audio_file is not None
    url = upload.track.listen_url
    response = api_client.get(url)
    assert response.status_code == 401


def test_upload_url_is_accessible_to_authenticated_users(
    logged_in_api_client, factories, preferences
):
    actor = logged_in_api_client.user.create_actor()
    preferences["common__api_authentication_required"] = True
    upload = factories["music.Upload"](library__actor=actor, import_status="finished")
    assert upload.audio_file is not None
    url = upload.track.listen_url
    response = logged_in_api_client.get(url)

    assert response.status_code == 200
    assert response["X-Accel-Redirect"] == "/_protected{}".format(upload.audio_file.url)
