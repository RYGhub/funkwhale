import pytest

from funkwhale_api.common import scripts
from funkwhale_api.common.management.commands import script


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


def test_django_permissions_to_user_permissions(factories, command):
    group = factories["auth.Group"](perms=["federation.change_library"])
    user1 = factories["users.User"](
        perms=[
            "dynamic_preferences.change_globalpreferencemodel",
            "music.add_importbatch",
        ]
    )
    user2 = factories["users.User"](perms=["music.add_importbatch"], groups=[group])

    scripts.django_permissions_to_user_permissions.main(command)

    user1.refresh_from_db()
    user2.refresh_from_db()

    assert user1.permission_settings is True
    assert user1.permission_library is True
    assert user1.permission_federation is False

    assert user2.permission_settings is False
    assert user2.permission_library is True
    assert user2.permission_federation is True


@pytest.mark.skip("Refactoring in progress")
def test_migrate_to_user_libraries(factories, command):
    user1 = factories["users.User"](is_superuser=False, with_actor=True)
    user2 = factories["users.User"](is_superuser=True, with_actor=True)
    factories["users.User"](is_superuser=True)
    no_import_files = factories["music.TrackFile"].create_batch(size=5, library=None)
    import_jobs = factories["music.ImportJob"].create_batch(
        batch__submitted_by=user1, size=5, finished=True
    )
    # we delete libraries that are created automatically
    for j in import_jobs:
        j.track_file.library = None
        j.track_file.save()
    scripts.migrate_to_user_libraries.main(command)

    # tracks with import jobs are bound to the importer's library
    library = user1.actor.libraries.get(name="default")
    assert list(library.files.order_by("id").values_list("id", flat=True)) == sorted(
        [ij.track_file.pk for ij in import_jobs]
    )

    # tracks without import jobs are bound to first superuser
    library = user2.actor.libraries.get(name="default")
    assert list(library.files.order_by("id").values_list("id", flat=True)) == sorted(
        [tf.pk for tf in no_import_files]
    )
