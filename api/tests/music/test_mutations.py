from funkwhale_api.music import licenses


def test_track_license_mutation(factories, now):
    track = factories["music.Track"](license=None)
    mutation = factories["common.Mutation"](
        type="update", target=track, payload={"license": "cc-by-sa-4.0"}
    )
    licenses.load(licenses.LICENSES)
    mutation.apply()
    track.refresh_from_db()

    assert track.license.code == "cc-by-sa-4.0"


def test_track_null_license_mutation(factories, now):
    track = factories["music.Track"](license="cc-by-sa-4.0")
    mutation = factories["common.Mutation"](
        type="update", target=track, payload={"license": None}
    )
    licenses.load(licenses.LICENSES)
    mutation.apply()
    track.refresh_from_db()

    assert track.license is None


def test_track_title_mutation(factories, now):
    track = factories["music.Track"](title="foo")
    mutation = factories["common.Mutation"](
        type="update", target=track, payload={"title": "bar"}
    )
    mutation.apply()
    track.refresh_from_db()

    assert track.title == "bar"


def test_track_copyright_mutation(factories, now):
    track = factories["music.Track"](copyright="foo")
    mutation = factories["common.Mutation"](
        type="update", target=track, payload={"copyright": "bar"}
    )
    mutation.apply()
    track.refresh_from_db()

    assert track.copyright == "bar"


def test_track_position_mutation(factories):
    track = factories["music.Track"](position=4)
    mutation = factories["common.Mutation"](
        type="update", target=track, payload={"position": 12}
    )
    mutation.apply()
    track.refresh_from_db()

    assert track.position == 12
