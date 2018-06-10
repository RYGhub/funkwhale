import pytest
from django.urls import reverse

from funkwhale_api.instance import views


@pytest.mark.parametrize("view,permissions", [(views.AdminSettings, ["settings"])])
def test_permissions(assert_user_permission, view, permissions):
    assert_user_permission(view, permissions)


def test_nodeinfo_endpoint(db, api_client, mocker):
    payload = {"test": "test"}
    mocked_nodeinfo = mocker.patch(
        "funkwhale_api.instance.nodeinfo.get", return_value=payload
    )
    url = reverse("api:v1:instance:nodeinfo-2.0")
    response = api_client.get(url)
    ct = "application/json; profile=http://nodeinfo.diaspora.software/ns/schema/2.0#; charset=utf-8"  # noqa
    assert response.status_code == 200
    assert response["Content-Type"] == ct
    assert response.data == payload


def test_nodeinfo_endpoint_disabled(db, api_client, preferences):
    preferences["instance__nodeinfo_enabled"] = False
    url = reverse("api:v1:instance:nodeinfo-2.0")
    response = api_client.get(url)

    assert response.status_code == 404


def test_settings_only_list_public_settings(db, api_client, preferences):
    url = reverse("api:v1:instance:settings")
    response = api_client.get(url)

    for conf in response.data:
        p = preferences.model.objects.get(section=conf["section"], name=conf["name"])
        assert p.preference.show_in_api is True


def test_admin_settings_restrict_access(db, logged_in_api_client, preferences):
    url = reverse("api:v1:instance:admin-settings-list")
    response = logged_in_api_client.get(url)

    assert response.status_code == 403


def test_admin_settings_correct_permission(db, logged_in_api_client, preferences):
    user = logged_in_api_client.user
    user.permission_settings = True
    user.save()
    url = reverse("api:v1:instance:admin-settings-list")
    response = logged_in_api_client.get(url)

    assert response.status_code == 200
    assert len(response.data) == len(preferences.all())
