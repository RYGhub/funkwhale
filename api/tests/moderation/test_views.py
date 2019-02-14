from django.urls import reverse


def test_restrict_to_own_filters(factories, logged_in_api_client):
    cf = factories["moderation.UserFilter"](
        for_artist=True, user=logged_in_api_client.user
    )
    factories["moderation.UserFilter"](for_artist=True)
    url = reverse("api:v1:moderation:content-filters-list")
    response = logged_in_api_client.get(url)
    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["uuid"] == str(cf.uuid)


def test_create_filter(factories, logged_in_api_client):
    artist = factories["music.Artist"]()
    url = reverse("api:v1:moderation:content-filters-list")
    data = {"target": {"type": "artist", "id": artist.pk}}
    response = logged_in_api_client.post(url, data, format="json")

    cf = logged_in_api_client.user.content_filters.latest("id")
    assert cf.target_artist == artist
    assert response.status_code == 201
