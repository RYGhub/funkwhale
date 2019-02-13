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
