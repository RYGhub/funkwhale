from funkwhale_api.tags import filters
from funkwhale_api.tags import models


def test_filter_search_tag(factories, queryset_equal_list):
    matches = [
        factories["tags.Tag"](name="Tag1"),
        factories["tags.Tag"](name="TestTag1"),
        factories["tags.Tag"](name="TestTag12"),
    ]
    factories["tags.Tag"](name="TestTag")
    factories["tags.Tag"](name="TestTag2")
    qs = models.Tag.objects.all().order_by("name")
    filterset = filters.TagFilter({"q": "tag1"}, queryset=qs)

    assert filterset.qs == matches
