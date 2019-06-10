import pytest

from funkwhale_api.common import utils


def test_chunk_queryset(factories):
    actors = factories["federation.Actor"].create_batch(size=4)
    queryset = actors[0].__class__.objects.all()
    chunks = list(utils.chunk_queryset(queryset, 2))

    assert list(chunks[0]) == actors[0:2]
    assert list(chunks[1]) == actors[2:4]


def test_update_prefix(factories):
    actors = []
    fid = "http://hello.world/actor/{}/"
    for i in range(3):
        actors.append(factories["federation.Actor"](fid=fid.format(i)))
    noop = [
        factories["federation.Actor"](fid="https://hello.world/actor/witness/"),
        factories["federation.Actor"](fid="http://another.world/actor/witness/"),
        factories["federation.Actor"](fid="http://foo.bar/actor/witness/"),
    ]

    qs = actors[0].__class__.objects.filter(fid__startswith="http://hello.world")
    assert qs.count() == 3

    result = utils.replace_prefix(
        actors[0].__class__.objects.all(),
        "fid",
        "http://hello.world",
        "https://hello.world",
    )

    assert result == 3

    for n in noop:
        old = n.fid
        n.refresh_from_db()
        assert old == n.fid

    for n in actors:
        old = n.fid
        n.refresh_from_db()
        assert n.fid == old.replace("http://", "https://")


@pytest.mark.parametrize(
    "conf, mock_args, data, expected",
    [
        (
            ["field1", "field2"],
            {"field1": "foo", "field2": "test"},
            {"field1": "bar"},
            {"field1": "bar"},
        ),
        (
            ["field1", "field2"],
            {"field1": "foo", "field2": "test"},
            {"field1": "foo"},
            {},
        ),
        (
            ["field1", "field2"],
            {"field1": "foo", "field2": "test"},
            {"field1": "foo", "field2": "test"},
            {},
        ),
        (
            ["field1", "field2"],
            {"field1": "foo", "field2": "test"},
            {"field1": "bar", "field2": "test1"},
            {"field1": "bar", "field2": "test1"},
        ),
        (
            [("field1", "Hello"), ("field2", "World")],
            {"Hello": "foo", "World": "test"},
            {"field1": "bar", "field2": "test1"},
            {"Hello": "bar", "World": "test1"},
        ),
    ],
)
def test_get_updated_fields(conf, mock_args, data, expected, mocker):
    obj = mocker.Mock(**mock_args)

    assert utils.get_updated_fields(conf, data, obj) == expected


@pytest.mark.parametrize(
    "start, end, expected",
    [
        ("https://domain", "/api", "https://domain/api"),
        ("https://domain/", "/api", "https://domain/api"),
        ("https://domain", "api", "https://domain/api"),
        ("https://domain", "https://api", "https://api"),
        ("https://domain", "http://api", "http://api"),
    ],
)
def test_join_url(start, end, expected):
    assert utils.join_url(start, end) == expected
