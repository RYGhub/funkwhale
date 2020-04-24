from funkwhale_api.music import models as music_models
from funkwhale_api.tags import tasks


def test_get_tags_from_foreign_key(factories):
    rock_tag = factories["tags.Tag"](name="Rock")
    rap_tag = factories["tags.Tag"](name="Rap")
    artist = factories["music.Artist"]()
    factories["music.Track"].create_batch(3, artist=artist, set_tags=["rock", "rap"])
    factories["music.Track"].create_batch(
        3, artist=artist, set_tags=["rock", "rap", "techno"]
    )

    result = tasks.get_tags_from_foreign_key(
        ids=[artist.pk],
        foreign_key_model=music_models.Track,
        foreign_key_attr="artist",
    )

    assert result == {artist.pk: [rock_tag.pk, rap_tag.pk]}


def test_add_tags_batch(factories):
    rock_tag = factories["tags.Tag"](name="Rock")
    rap_tag = factories["tags.Tag"](name="Rap")
    factories["tags.Tag"]()
    artist = factories["music.Artist"]()

    data = {artist.pk: [rock_tag.pk, rap_tag.pk]}

    tasks.add_tags_batch(
        data, model=artist.__class__,
    )

    assert artist.get_tags() == ["Rap", "Rock"]
