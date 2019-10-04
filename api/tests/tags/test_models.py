import pytest

from funkwhale_api.tags import models


@pytest.mark.parametrize(
    "existing, given, expected",
    [
        ([], ["tag1"], ["tag1"]),
        (["tag1"], ["tag1"], ["tag1"]),
        (["tag1"], ["tag2"], ["tag1", "tag2"]),
        (["tag1"], ["tag2", "tag3"], ["tag1", "tag2", "tag3"]),
    ],
)
def test_add_tags(factories, existing, given, expected):
    obj = factories["music.Artist"]()
    for tag in existing:
        factories["tags.TaggedItem"](content_object=obj, tag__name=tag)

    models.add_tags(obj, *given)

    tagged_items = models.TaggedItem.objects.all()

    assert tagged_items.count() == len(expected)
    for tag in expected:
        match = tagged_items.get(tag__name=tag)
        assert match.content_object == obj


@pytest.mark.parametrize(
    "existing, given, expected",
    [
        ([], ["tag1"], ["tag1"]),
        (["tag1"], ["tag1"], ["tag1"]),
        (["tag1"], [], []),
        (["tag1"], ["tag2"], ["tag2"]),
        (["tag1", "tag2"], ["tag2"], ["tag2"]),
        (["tag1", "tag2"], ["tag3", "tag4"], ["tag3", "tag4"]),
    ],
)
def test_set_tags(factories, existing, given, expected):
    obj = factories["music.Artist"]()
    for tag in existing:
        factories["tags.TaggedItem"](content_object=obj, tag__name=tag)

    models.set_tags(obj, *given)

    tagged_items = models.TaggedItem.objects.all()

    assert tagged_items.count() == len(expected)
    for tag in expected:
        match = tagged_items.get(tag__name=tag)
        assert match.content_object == obj


@pytest.mark.parametrize(
    "max, tags, expected",
    [
        (5, ["hello", "world"], ["hello", "world"]),
        # we truncate extra tags
        (1, ["hello", "world"], ["hello"]),
        (2, ["hello", "world", "foo"], ["hello", "world"]),
    ],
)
def test_set_tags_honor_TAGS_MAX_BY_OBJ(factories, max, tags, expected, settings):
    settings.TAGS_MAX_BY_OBJ = max
    obj = factories["music.Artist"]()

    models.set_tags(obj, *tags)

    assert sorted(obj.tagged_items.values_list("tag__name", flat=True)) == expected


@pytest.mark.parametrize("factory_name", ["music.Track", "music.Album", "music.Artist"])
def test_models_that_support_tags(factories, factory_name):
    tags = ["tag1", "tag2"]
    obj = factories[factory_name](set_tags=tags)

    assert sorted(obj.tagged_items.all().values_list("tag__name", flat=True)) == tags
