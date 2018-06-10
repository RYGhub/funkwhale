import json

from django.urls import reverse

from funkwhale_api.music.serializers import TrackSerializer
from funkwhale_api.radios import filters, serializers


def test_can_list_config_options(logged_in_client):
    url = reverse("api:v1:radios:radios-filters")
    response = logged_in_client.get(url)

    assert response.status_code == 200

    payload = json.loads(response.content.decode("utf-8"))

    expected = [f for f in filters.registry.values() if f.expose_in_api]
    assert len(payload) == len(expected)


def test_can_validate_config(logged_in_client, factories):
    artist1 = factories["music.Artist"]()
    artist2 = factories["music.Artist"]()
    factories["music.Track"].create_batch(3, artist=artist1)
    factories["music.Track"].create_batch(3, artist=artist2)
    candidates = artist1.tracks.order_by("pk")
    f = {"filters": [{"type": "artist", "ids": [artist1.pk]}]}
    url = reverse("api:v1:radios:radios-validate")
    response = logged_in_client.post(
        url, json.dumps(f), content_type="application/json"
    )

    assert response.status_code == 200

    payload = json.loads(response.content.decode("utf-8"))

    expected = {
        "count": candidates.count(),
        "sample": TrackSerializer(candidates, many=True).data,
    }
    assert payload["filters"][0]["candidates"] == expected
    assert payload["filters"][0]["errors"] == []


def test_can_validate_config_with_wrong_config(logged_in_client, factories):
    f = {"filters": [{"type": "artist", "ids": [999]}]}
    url = reverse("api:v1:radios:radios-validate")
    response = logged_in_client.post(
        url, json.dumps(f), content_type="application/json"
    )

    assert response.status_code == 200

    payload = json.loads(response.content.decode("utf-8"))

    expected = {"count": None, "sample": None}
    assert payload["filters"][0]["candidates"] == expected
    assert len(payload["filters"][0]["errors"]) == 1


def test_saving_radio_sets_user(logged_in_client, factories):
    artist = factories["music.Artist"]()
    f = {"name": "Test", "config": [{"type": "artist", "ids": [artist.pk]}]}
    url = reverse("api:v1:radios:radios-list")
    response = logged_in_client.post(
        url, json.dumps(f), content_type="application/json"
    )

    assert response.status_code == 201

    radio = logged_in_client.user.radios.latest("id")
    assert radio.name == "Test"
    assert radio.user == logged_in_client.user


def test_user_can_detail_his_radio(logged_in_client, factories):
    radio = factories["radios.Radio"](user=logged_in_client.user)
    url = reverse("api:v1:radios:radios-detail", kwargs={"pk": radio.pk})
    response = logged_in_client.get(url)

    assert response.status_code == 200


def test_user_can_detail_public_radio(logged_in_client, factories):
    radio = factories["radios.Radio"](is_public=True)
    url = reverse("api:v1:radios:radios-detail", kwargs={"pk": radio.pk})
    response = logged_in_client.get(url)

    assert response.status_code == 200


def test_user_cannot_detail_someone_else_radio(logged_in_client, factories):
    radio = factories["radios.Radio"](is_public=False)
    url = reverse("api:v1:radios:radios-detail", kwargs={"pk": radio.pk})
    response = logged_in_client.get(url)

    assert response.status_code == 404


def test_user_can_edit_his_radio(logged_in_client, factories):
    radio = factories["radios.Radio"](user=logged_in_client.user)
    url = reverse("api:v1:radios:radios-detail", kwargs={"pk": radio.pk})
    response = logged_in_client.put(
        url, json.dumps({"name": "new", "config": []}), content_type="application/json"
    )

    radio.refresh_from_db()
    assert response.status_code == 200
    assert radio.name == "new"


def test_user_cannot_edit_someone_else_radio(logged_in_client, factories):
    radio = factories["radios.Radio"]()
    url = reverse("api:v1:radios:radios-detail", kwargs={"pk": radio.pk})
    response = logged_in_client.put(
        url, json.dumps({"name": "new", "config": []}), content_type="application/json"
    )

    assert response.status_code == 404


def test_clean_config_is_called_on_serializer_save(mocker, factories):
    user = factories["users.User"]()
    artist = factories["music.Artist"]()
    data = {"name": "Test", "config": [{"type": "artist", "ids": [artist.pk]}]}
    spied = mocker.spy(filters.registry["artist"], "clean_config")
    serializer = serializers.RadioSerializer(data=data)
    assert serializer.is_valid()
    instance = serializer.save(user=user)
    spied.assert_called_once_with(data["config"][0])
    assert instance.config[0]["names"] == [artist.name]
