import pytest
from django.core.exceptions import ValidationError

from funkwhale_api.music.models import Track
from funkwhale_api.radios import filters


@filters.registry.register
class NoopFilter(filters.RadioFilter):
    code = "noop"

    def get_query(self, candidates, **kwargs):
        return


def test_most_simple_radio_does_not_filter_anything(factories):
    factories["music.Track"].create_batch(3)
    radio = factories["radios.Radio"](config=[{"type": "noop"}])

    assert radio.version == 0
    assert radio.get_candidates().count() == 3


def test_filter_can_use_custom_queryset(factories):
    tracks = factories["music.Track"].create_batch(3)
    candidates = Track.objects.filter(pk=tracks[0].pk)

    qs = filters.run([{"type": "noop"}], candidates=candidates)
    assert qs.count() == 1
    assert qs.first() == tracks[0]


def test_filter_on_tag(factories):
    tracks = factories["music.Track"].create_batch(3, tags=["metal"])
    factories["music.Track"].create_batch(3, tags=["pop"])
    expected = tracks
    f = [{"type": "tag", "names": ["metal"]}]

    candidates = filters.run(f)
    assert list(candidates.order_by("pk")) == expected


def test_filter_on_artist(factories):
    artist1 = factories["music.Artist"]()
    artist2 = factories["music.Artist"]()
    factories["music.Track"].create_batch(3, artist=artist1)
    factories["music.Track"].create_batch(3, artist=artist2)
    expected = list(artist1.tracks.order_by("pk"))
    f = [{"type": "artist", "ids": [artist1.pk]}]

    candidates = filters.run(f)
    assert list(candidates.order_by("pk")) == expected


def test_can_combine_with_or(factories):
    artist1 = factories["music.Artist"]()
    artist2 = factories["music.Artist"]()
    artist3 = factories["music.Artist"]()
    factories["music.Track"].create_batch(3, artist=artist1)
    factories["music.Track"].create_batch(3, artist=artist2)
    factories["music.Track"].create_batch(3, artist=artist3)
    expected = Track.objects.exclude(artist=artist3).order_by("pk")
    f = [
        {"type": "artist", "ids": [artist1.pk]},
        {"type": "artist", "ids": [artist2.pk], "operator": "or"},
    ]

    candidates = filters.run(f)
    assert list(candidates.order_by("pk")) == list(expected)


def test_can_combine_with_and(factories):
    artist1 = factories["music.Artist"]()
    artist2 = factories["music.Artist"]()
    metal_tracks = factories["music.Track"].create_batch(
        2, artist=artist1, tags=["metal"]
    )
    factories["music.Track"].create_batch(2, artist=artist1, tags=["pop"])
    factories["music.Track"].create_batch(3, artist=artist2)
    expected = metal_tracks
    f = [
        {"type": "artist", "ids": [artist1.pk]},
        {"type": "tag", "names": ["metal"], "operator": "and"},
    ]

    candidates = filters.run(f)
    assert list(candidates.order_by("pk")) == list(expected)


def test_can_negate(factories):
    artist1 = factories["music.Artist"]()
    artist2 = factories["music.Artist"]()
    factories["music.Track"].create_batch(3, artist=artist1)
    factories["music.Track"].create_batch(3, artist=artist2)
    expected = artist2.tracks.order_by("pk")
    f = [{"type": "artist", "ids": [artist1.pk], "not": True}]

    candidates = filters.run(f)
    assert list(candidates.order_by("pk")) == list(expected)


def test_can_group(factories):
    artist1 = factories["music.Artist"]()
    artist2 = factories["music.Artist"]()
    factories["music.Track"].create_batch(2, artist=artist1)
    t1 = factories["music.Track"].create_batch(2, artist=artist1, tags=["metal"])
    factories["music.Track"].create_batch(2, artist=artist2)
    t2 = factories["music.Track"].create_batch(2, artist=artist2, tags=["metal"])
    factories["music.Track"].create_batch(2, tags=["metal"])
    expected = t1 + t2
    f = [
        {"type": "tag", "names": ["metal"]},
        {
            "type": "group",
            "operator": "and",
            "filters": [
                {"type": "artist", "ids": [artist1.pk], "operator": "or"},
                {"type": "artist", "ids": [artist2.pk], "operator": "or"},
            ],
        },
    ]

    candidates = filters.run(f)
    assert list(candidates.order_by("pk")) == list(expected)


def test_artist_filter_clean_config(factories):
    artist1 = factories["music.Artist"]()
    artist2 = factories["music.Artist"]()

    config = filters.clean_config({"type": "artist", "ids": [artist2.pk, artist1.pk]})

    expected = {
        "type": "artist",
        "ids": [artist1.pk, artist2.pk],
        "names": [artist1.name, artist2.name],
    }
    assert filters.clean_config(config) == expected


def test_can_check_artist_filter(factories):
    artist = factories["music.Artist"]()

    assert filters.validate({"type": "artist", "ids": [artist.pk]})
    with pytest.raises(ValidationError):
        filters.validate({"type": "artist", "ids": [artist.pk + 1]})


def test_can_check_operator():
    assert filters.validate({"type": "group", "operator": "or", "filters": []})
    assert filters.validate({"type": "group", "operator": "and", "filters": []})
    with pytest.raises(ValidationError):
        assert filters.validate({"type": "group", "operator": "nope", "filters": []})
