from funkwhale_api.federation import fields
from funkwhale_api.federation import filters
from funkwhale_api.federation import models


def test_inbox_item_filter_before(factories):
    expected = models.InboxItem.objects.filter(pk__lte=12)
    f = filters.InboxItemFilter({"before": 12}, queryset=models.InboxItem.objects.all())

    assert str(f.qs.query) == str(expected.query)


def test_domain_from_url_filter(factories):
    found = [
        factories["music.Artist"](fid="http://domain/test1"),
        factories["music.Artist"](fid="https://domain/test2"),
    ]
    factories["music.Artist"](fid="http://domain2/test1")
    factories["music.Artist"](fid="https://otherdomain/test2")

    queryset = found[0].__class__.objects.all().order_by("id")
    field = fields.DomainFromURLFilter()
    result = field.filter(queryset, "domain")
    assert list(result) == found
