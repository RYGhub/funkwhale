import pytest

from django.urls import reverse

from funkwhale_api.federation import utils as federation_utils


@pytest.mark.parametrize(
    "model,factory_args,namespace",
    [("common.Mutation", {"created_by__local": True}, "federation:edits-detail")],
)
def test_mutation_fid_is_populated(factories, model, factory_args, namespace):
    instance = factories[model](**factory_args, fid=None, payload={})

    assert instance.fid == federation_utils.full_url(
        reverse(namespace, kwargs={"uuid": instance.uuid})
    )


@pytest.mark.parametrize(
    "factory_name, expected",
    [
        ("music.Artist", "/library/artists/{obj.pk}"),
        ("music.Album", "/library/albums/{obj.pk}"),
        ("music.Track", "/library/tracks/{obj.pk}"),
        ("playlists.Playlist", "/library/playlists/{obj.pk}"),
    ],
)
def test_get_absolute_url(factory_name, factories, expected):
    obj = factories[factory_name]()

    assert obj.get_absolute_url() == expected.format(obj=obj)


@pytest.mark.parametrize(
    "factory_name, expected",
    [
        ("music.Artist", "/manage/library/artists/{obj.pk}"),
        ("music.Album", "/manage/library/albums/{obj.pk}"),
        ("music.Track", "/manage/library/tracks/{obj.pk}"),
        ("music.Library", "/manage/library/libraries/{obj.uuid}"),
        ("federation.Actor", "/manage/moderation/accounts/{obj.full_username}"),
    ],
)
def test_get_moderation_url(factory_name, factories, expected):
    obj = factories[factory_name]()

    assert obj.get_moderation_url() == expected.format(obj=obj)
