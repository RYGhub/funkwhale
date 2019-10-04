from django.urls import reverse

from funkwhale_api.tags import serializers


def test_tags_list(factories, logged_in_api_client):
    url = reverse("api:v1:tags-list")
    tag = factories["tags.Tag"]()

    expected = {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [serializers.TagSerializer(tag).data],
    }

    response = logged_in_api_client.get(url)

    assert response.data == expected


def test_tags_list_ordering_length(factories, logged_in_api_client):
    url = reverse("api:v1:tags-list")
    tags = [
        factories["tags.Tag"](name="iamareallylongtag"),
        factories["tags.Tag"](name="short"),
        factories["tags.Tag"](name="reallylongtag"),
        factories["tags.Tag"](name="bar"),
    ]
    expected = {
        "count": 4,
        "next": None,
        "previous": None,
        "results": [
            serializers.TagSerializer(tag).data
            for tag in [tags[3], tags[1], tags[2], tags[0]]
        ],
    }

    response = logged_in_api_client.get(url, {"ordering": "length"})

    assert response.data == expected


def test_tags_detail(factories, logged_in_api_client):
    tag = factories["tags.Tag"]()
    url = reverse("api:v1:tags-detail", kwargs={"name": tag.name})

    expected = serializers.TagSerializer(tag).data

    response = logged_in_api_client.get(url)

    assert response.data == expected
