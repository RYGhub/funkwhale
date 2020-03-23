import datetime
import pytest

from funkwhale_api.common import serializers as common_serializers
from funkwhale_api.music import licenses
from funkwhale_api.music import mutations

from funkwhale_api.tags import models as tags_models


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


@pytest.mark.parametrize("factory_name", ["music.Artist", "music.Album", "music.Track"])
def test_mutation_set_tags(factory_name, factories, now, mocker):
    tags = ["tag1", "tag2"]
    dispatch = mocker.patch("funkwhale_api.federation.routes.outbox.dispatch")
    set_tags = mocker.spy(tags_models, "set_tags")
    obj = factories[factory_name]()
    assert obj.tagged_items.all().count() == 0
    mutation = factories["common.Mutation"](
        type="update", target=obj, payload={"tags": tags}
    )
    mutation.apply()
    obj.refresh_from_db()

    assert sorted(obj.tagged_items.all().values_list("tag__name", flat=True)) == tags
    set_tags.assert_called_once_with(obj, *tags)
    obj_type = factory_name.lstrip("music.")
    dispatch.assert_called_once_with(
        {"type": "Update", "object": {"type": obj_type}},
        context={obj_type.lower(): obj},
    )


@pytest.mark.parametrize("is_local, expected", [(True, True), (False, False)])
def test_perm_checkers_can_suggest(factories, is_local, expected):
    obj = factories["music.Track"](local=is_local)
    assert mutations.can_suggest(obj, actor=None) is expected


@pytest.mark.parametrize(
    "is_local, permission_library, actor_is_attributed, expected",
    [
        # Not local object, so local users can't edit
        (False, False, False, False),
        (False, True, False, False),
        # Local but no specific conditions met for permission
        (True, False, False, False),
        # Local and attributed_to -> ok
        (True, False, True, True),
        # Local and library permission -> ok
        (True, True, False, True),
    ],
)
def test_perm_checkers_can_approve(
    factories, is_local, permission_library, actor_is_attributed, expected
):
    actor = factories["users.User"](
        permission_library=permission_library
    ).create_actor()
    obj_kwargs = {"local": is_local}
    if actor_is_attributed:
        obj_kwargs["attributed_to"] = actor
    obj = factories["music.Track"](**obj_kwargs)

    assert mutations.can_approve(obj, actor=actor) is expected


@pytest.mark.parametrize("factory_name", ["music.Artist", "music.Track", "music.Album"])
def test_mutation_set_attachment_cover(factory_name, factories, now, mocker):
    new_attachment = factories["common.Attachment"](actor__local=True)
    obj = factories[factory_name](with_cover=True)
    old_attachment = obj.attachment_cover
    mutation = factories["common.Mutation"](
        type="update", target=obj, payload={"cover": new_attachment.uuid}
    )

    # new attachment should be linked to mutation, to avoid being pruned
    # before being applied
    assert new_attachment.mutation_attachment.mutation == mutation

    mutation.apply()
    obj.refresh_from_db()

    assert obj.attachment_cover == new_attachment
    assert mutation.previous_state["cover"] == old_attachment.uuid


@pytest.mark.parametrize(
    "factory_name", ["music.Track", "music.Album", "music.Artist"],
)
def test_album_mutation_description(factory_name, factories, mocker):
    mocker.patch("funkwhale_api.federation.routes.outbox.dispatch")
    content = factories["common.Content"]()
    obj = factories[factory_name](description=content)
    mutation = factories["common.Mutation"](
        type="update",
        target=obj,
        payload={"description": {"content_type": "text/plain", "text": "hello there"}},
    )
    mutation.apply()
    obj.refresh_from_db()

    assert obj.description.content_type == "text/plain"
    assert obj.description.text == "hello there"
    assert (
        mutation.previous_state["description"]
        == common_serializers.ContentSerializer(content).data
    )
