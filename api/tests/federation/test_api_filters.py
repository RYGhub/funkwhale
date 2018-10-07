from funkwhale_api.federation import filters
from funkwhale_api.federation import models


def test_inbox_item_filter_before(factories):
    expected = models.InboxItem.objects.filter(pk__lte=12)
    f = filters.InboxItemFilter({"before": 12}, queryset=models.InboxItem.objects.all())

    assert str(f.qs.query) == str(expected.query)
