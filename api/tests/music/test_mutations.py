import datetime
import pytest

from funkwhale_api.music import licenses


@pytest.mark.parametrize(
    "field, old_value, new_value, expected", [("name", "foo", "bar", "bar")]
)
def test_artist_mutation(field, old_value, new_value, expected, factories, now, mocker):
    dispatch = mocker.patch("funkwhale_api.federation.routes.outbox.dispatch")
    artist = factories["music.Artist"](**{field: old_value})
    mutation = factories["common.Mutation"](
        type="update", target=artist, payload={field: new_value}
    )
    mutation.apply()
    artist.refresh_from_db()

    assert getattr(artist, field) == expected
    dispatch.assert_called_once_with(
        {"type": "Update", "object": {"type": "Artist"}}, context={"artist": artist}
    )


@pytest.mark.parametrize(
    "field, old_value, new_value, expected",
    [
        ("title", "foo", "bar", "bar"),
        (
            "release_date",
            datetime.date(2016, 1, 1),
            "2018-02-01",
            datetime.date(2018, 2, 1),
        ),
    ],
)
def test_album_mutation(field, old_value, new_value, expected, factories, now, mocker):
    dispatch = mocker.patch("funkwhale_api.federation.routes.outbox.dispatch")
    album = factories["music.Album"](**{field: old_value})
    mutation = factories["common.Mutation"](
        type="update", target=album, payload={field: new_value}
    )
    mutation.apply()
    album.refresh_from_db()

    assert getattr(album, field) == expected
    dispatch.assert_called_once_with(
        {"type": "Update", "object": {"type": "Album"}}, context={"album": album}
    )


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


def test_track_mutation_apply_outbox(factories, mocker):
    dispatch = mocker.patch("funkwhale_api.federation.routes.outbox.dispatch")
    track = factories["music.Track"](position=4)
    mutation = factories["common.Mutation"](
        type="update", target=track, payload={"position": 12}
    )
    mutation.apply()

    dispatch.assert_called_once_with(
        {"type": "Update", "object": {"type": "Track"}}, context={"track": track}
    )
