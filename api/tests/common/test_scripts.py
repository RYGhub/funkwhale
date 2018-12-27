import pytest

from funkwhale_api.common import scripts
from funkwhale_api.common.management.commands import script
from funkwhale_api.federation import models as federation_models
from funkwhale_api.music import models as music_models


@pytest.fixture
def command():
    return script.Command()


@pytest.mark.parametrize(
    "script_name", ["django_permissions_to_user_permissions", "test"]
)
def test_script_command_list(command, script_name, mocker):
    mocked = mocker.patch("funkwhale_api.common.scripts.{}.main".format(script_name))

    command.handle(script_name=script_name, interactive=False)

    mocked.assert_called_once_with(command, script_name=script_name, interactive=False)


@pytest.mark.parametrize(
    "open_api,expected_visibility", [(True, "everyone"), (False, "instance")]
)
def test_migrate_to_user_libraries_create_libraries(
    factories, open_api, expected_visibility, stdout
):
    user1 = factories["users.User"](with_actor=True)
    user2 = factories["users.User"](with_actor=True)

    result = scripts.migrate_to_user_libraries.create_libraries(open_api, stdout)

    user1_library = user1.actor.libraries.get(
        name="default", privacy_level=expected_visibility
    )
    user2_library = user2.actor.libraries.get(
        name="default", privacy_level=expected_visibility
    )

    assert result == {user1.pk: user1_library.pk, user2.pk: user2_library.pk}


def test_migrate_to_user_libraries_update_uploads(factories, stdout):
    user1 = factories["users.User"](with_actor=True)
    user2 = factories["users.User"](with_actor=True)

    library1 = factories["music.Library"](actor=user1.actor)
    library2 = factories["music.Library"](actor=user2.actor)

    upload1 = factories["music.Upload"]()
    upload2 = factories["music.Upload"]()

    # we delete libraries
    upload1.library = None
    upload2.library = None
    upload1.save()
    upload2.save()

    factories["music.ImportJob"](batch__submitted_by=user1, upload=upload1)
    factories["music.ImportJob"](batch__submitted_by=user2, upload=upload2)

    libraries_by_user = {user1.pk: library1.pk, user2.pk: library2.pk}

    scripts.migrate_to_user_libraries.update_uploads(libraries_by_user, stdout)

    upload1.refresh_from_db()
    upload2.refresh_from_db()

    assert upload1.library == library1
    assert upload1.import_status == "finished"
    assert upload2.library == library2
    assert upload2.import_status == "finished"


@pytest.mark.parametrize(
    "open_api,expected_visibility", [(True, "everyone"), (False, "instance")]
)
def test_migrate_to_user_libraries_without_jobs(
    factories, open_api, expected_visibility, stdout
):
    superuser = factories["users.User"](is_superuser=True, with_actor=True)
    upload1 = factories["music.Upload"]()
    upload2 = factories["music.Upload"]()
    upload3 = factories["music.Upload"](audio_file=None)

    # we delete libraries
    upload1.library = None
    upload2.library = None
    upload3.library = None
    upload1.save()
    upload2.save()
    upload3.save()

    factories["music.ImportJob"](upload=upload2)
    scripts.migrate_to_user_libraries.update_orphan_uploads(open_api, stdout)

    upload1.refresh_from_db()
    upload2.refresh_from_db()
    upload3.refresh_from_db()

    superuser_library = superuser.actor.libraries.get(
        name="default", privacy_level=expected_visibility
    )
    assert upload1.library == superuser_library
    assert upload1.import_status == "finished"
    # left untouched because they don't match filters
    assert upload2.library is None
    assert upload3.library is None


@pytest.mark.parametrize(
    "model,args,path",
    [
        ("music.Upload", {"library__actor__local": True}, "/federation/music/uploads/"),
        ("music.Artist", {}, "/federation/music/artists/"),
        ("music.Album", {}, "/federation/music/albums/"),
        ("music.Track", {}, "/federation/music/tracks/"),
    ],
)
def test_migrate_to_user_libraries_generate_fids(
    factories, args, model, path, settings, stdout
):
    template = "{}{}{}"

    objects = factories[model].create_batch(5, fid=None, **args)
    klass = factories[model]._meta.model

    # we leave a fid on the first one, and set the others to None
    existing_fid = objects[0].fid
    base_path = existing_fid.replace(str(objects[0].uuid), "")
    klass.objects.filter(pk__in=[o.pk for o in objects[1:]]).update(fid=None)

    scripts.migrate_to_user_libraries.set_fid(klass.objects.all(), path, stdout)

    for i, o in enumerate(objects):
        o.refresh_from_db()
        if i == 0:
            assert o.fid == existing_fid
        else:
            assert o.fid == template.format(settings.FUNKWHALE_URL, path, o.uuid)
            # we also ensure the path we insert match the one that is generated
            # by the app on objects creation, as a safe guard for typos
            assert base_path == o.fid.replace(str(o.uuid), "")


def test_migrate_to_user_libraries_update_actors_shared_inbox_url(factories, stdout):
    local = factories["federation.Actor"](local=True, shared_inbox_url=None)
    remote = factories["federation.Actor"](local=False, shared_inbox_url=None)
    expected = federation_models.get_shared_inbox_url()
    scripts.migrate_to_user_libraries.update_shared_inbox_url(stdout)

    local.refresh_from_db()
    remote.refresh_from_db()

    assert local.shared_inbox_url == expected
    assert remote.shared_inbox_url is None


@pytest.mark.parametrize("part", ["following", "followers"])
def test_migrate_to_user_libraries_generate_actor_urls(
    factories, part, settings, stdout
):
    field = "{}_url".format(part)
    ok = factories["users.User"]().create_actor()
    local = factories["federation.Actor"](local=True, **{field: None})
    remote = factories["federation.Actor"](local=False, **{field: None})

    assert getattr(local, field) is None
    expected = "{}/federation/actors/{}/{}".format(
        settings.FUNKWHALE_URL, local.preferred_username, part
    )
    ok_url = getattr(ok, field)

    scripts.migrate_to_user_libraries.generate_actor_urls(part, stdout)

    ok.refresh_from_db()
    local.refresh_from_db()
    remote.refresh_from_db()

    # unchanged
    assert getattr(ok, field) == ok_url
    assert getattr(remote, field) is None

    assert getattr(local, field) == expected
    assert expected.replace(local.preferred_username, "") == ok_url.replace(
        ok.preferred_username, ""
    )


def test_migrate_to_users_libraries_command(
    preferences, mocker, db, command, queryset_equal_queries
):
    preferences["common__api_authentication_required"] = False
    open_api = not preferences["common__api_authentication_required"]
    create_libraries = mocker.patch.object(
        scripts.migrate_to_user_libraries,
        "create_libraries",
        return_value={"hello": "world"},
    )
    update_uploads = mocker.patch.object(
        scripts.migrate_to_user_libraries, "update_uploads"
    )
    update_orphan_uploads = mocker.patch.object(
        scripts.migrate_to_user_libraries, "update_orphan_uploads"
    )
    set_fid = mocker.patch.object(scripts.migrate_to_user_libraries, "set_fid")
    update_shared_inbox_url = mocker.patch.object(
        scripts.migrate_to_user_libraries, "update_shared_inbox_url"
    )
    generate_actor_urls = mocker.patch.object(
        scripts.migrate_to_user_libraries, "generate_actor_urls"
    )

    scripts.migrate_to_user_libraries.main(command)

    create_libraries.assert_called_once_with(open_api, command.stdout)
    update_uploads.assert_called_once_with({"hello": "world"}, command.stdout)
    update_orphan_uploads.assert_called_once_with(open_api, command.stdout)
    set_fid_params = [
        (
            music_models.Upload.objects.exclude(library__actor__user=None),
            "/federation/music/uploads/",
        ),
        (music_models.Artist.objects.all(), "/federation/music/artists/"),
        (music_models.Album.objects.all(), "/federation/music/albums/"),
        (music_models.Track.objects.all(), "/federation/music/tracks/"),
    ]
    for qs, path in set_fid_params:
        set_fid.assert_any_call(qs, path, command.stdout)
    update_shared_inbox_url.assert_called_once_with(command.stdout)
    # generate_actor_urls(part, stdout):

    for part in ["followers", "following"]:
        generate_actor_urls.assert_any_call(part, command.stdout)
