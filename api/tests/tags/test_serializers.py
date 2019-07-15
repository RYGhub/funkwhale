import pytest

from funkwhale_api.tags import serializers


def test_tag_serializer(factories):
    tag = factories["tags.Tag"]()

    serializer = serializers.TagSerializer(tag)

    expected = {
        "name": tag.name,
        "creation_date": tag.creation_date.isoformat().split("+")[0] + "Z",
    }

    assert serializer.data == expected


@pytest.mark.parametrize(
    "name",
    [
        "",
        "invalid because spaces",
        "invalid-because-dashes",
        "invalid because non breaking spaces",
    ],
)
def test_tag_name_field_validation(name):
    field = serializers.TagNameField()
    with pytest.raises(serializers.serializers.ValidationError):
        field.to_internal_value(name)


@pytest.mark.parametrize(
    "max, tags, expected",
    [
        (5, ["hello", "world"], ["hello", "world"]),
        # we truncate extra tags
        (1, ["hello", "world"], ["hello"]),
        (2, ["hello", "world", "foo"], ["hello", "world"]),
    ],
)
def test_tags_list_field_honor_TAGS_MAX_BY_OBJ(max, tags, expected, settings):
    settings.TAGS_MAX_BY_OBJ = max
    field = serializers.TagsListField()
    assert field.to_internal_value(tags) == expected
