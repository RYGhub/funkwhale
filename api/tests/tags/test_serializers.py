from funkwhale_api.tags import serializers


def test_tag_serializer(factories):
    tag = factories["tags.Tag"]()

    serializer = serializers.TagSerializer(tag)

    expected = {
        "name": tag.name,
        "creation_date": tag.creation_date.isoformat().split("+")[0] + "Z",
    }

    assert serializer.data == expected
