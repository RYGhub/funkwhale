from funkwhale_api.common import utils


def test_chunk_queryset(factories):
    actors = factories["federation.Actor"].create_batch(size=4)
    queryset = actors[0].__class__.objects.all()
    chunks = list(utils.chunk_queryset(queryset, 2))

    assert list(chunks[0]) == actors[0:2]
    assert list(chunks[1]) == actors[2:4]
