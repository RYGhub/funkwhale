import os

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")


def test_management_command_requires_a_valid_library_id(factories):
    path = os.path.join(DATA_DIR, "dummy_file.ogg")

    with pytest.raises(CommandError) as e:
        call_command("import_files", "wrong_id", path, interactive=False)
    assert "Invalid library id" in str(e)


def test_in_place_import_only_from_music_dir(factories, settings):
    library = factories["music.Library"](actor__local=True)
    settings.MUSIC_DIRECTORY_PATH = "/nope"
    path = os.path.join(DATA_DIR, "dummy_file.ogg")
    with pytest.raises(CommandError) as e:
        call_command(
            "import_files", str(library.uuid), path, in_place=True, interactive=False
        )

    assert "Importing in-place only works if importing" in str(e)


def test_import_with_multiple_argument(factories, mocker):
    library = factories["music.Library"](actor__local=True)
    path1 = os.path.join(DATA_DIR, "dummy_file.ogg")
    path2 = os.path.join(DATA_DIR, "utf8-éà◌.ogg")
    mocked_filter = mocker.patch(
        "funkwhale_api.providers.audiofile.management.commands.import_files.Command.filter_matching",
        return_value=({"new": [], "skipped": []}),
    )
    call_command("import_files", str(library.uuid), path1, path2, interactive=False)
    mocked_filter.assert_called_once_with([path1, path2], library)


@pytest.mark.parametrize(
    "path",
    [os.path.join(DATA_DIR, "dummy_file.ogg"), os.path.join(DATA_DIR, "utf8-éà◌.ogg")],
)
def test_import_files_stores_proper_data(factories, mocker, now, path):
    mocked_process = mocker.patch("funkwhale_api.music.tasks.process_upload")
    library = factories["music.Library"](actor__local=True)
    call_command(
        "import_files", str(library.uuid), path, async_=False, interactive=False
    )
    upload = library.uploads.last()
    assert upload.import_reference == "cli-{}".format(now.isoformat())
    assert upload.import_status == "pending"
    assert upload.source == "file://{}".format(path)
    assert upload.import_metadata == {
        "funkwhale": {
            "config": {"replace": False, "dispatch_outbox": False, "broadcast": False}
        }
    }

    mocked_process.assert_called_once_with(upload_id=upload.pk)


def test_import_with_outbox_flag(factories, mocker):
    library = factories["music.Library"](actor__local=True)
    path = os.path.join(DATA_DIR, "dummy_file.ogg")
    mocked_process = mocker.patch("funkwhale_api.music.tasks.process_upload")
    call_command(
        "import_files", str(library.uuid), path, outbox=True, interactive=False
    )
    upload = library.uploads.last()

    assert upload.import_metadata["funkwhale"]["config"]["dispatch_outbox"] is True

    mocked_process.assert_called_once_with(upload_id=upload.pk)


def test_import_with_broadcast_flag(factories, mocker):
    library = factories["music.Library"](actor__local=True)
    path = os.path.join(DATA_DIR, "dummy_file.ogg")
    mocked_process = mocker.patch("funkwhale_api.music.tasks.process_upload")
    call_command(
        "import_files", str(library.uuid), path, broadcast=True, interactive=False
    )
    upload = library.uploads.last()

    assert upload.import_metadata["funkwhale"]["config"]["broadcast"] is True

    mocked_process.assert_called_once_with(upload_id=upload.pk)


def test_import_with_replace_flag(factories, mocker):
    library = factories["music.Library"](actor__local=True)
    path = os.path.join(DATA_DIR, "dummy_file.ogg")
    mocked_process = mocker.patch("funkwhale_api.music.tasks.process_upload")
    call_command(
        "import_files", str(library.uuid), path, replace=True, interactive=False
    )
    upload = library.uploads.last()

    assert upload.import_metadata["funkwhale"]["config"]["replace"] is True

    mocked_process.assert_called_once_with(upload_id=upload.pk)


def test_import_with_custom_reference(factories, mocker):
    library = factories["music.Library"](actor__local=True)
    path = os.path.join(DATA_DIR, "dummy_file.ogg")
    mocked_process = mocker.patch("funkwhale_api.music.tasks.process_upload")
    call_command(
        "import_files",
        str(library.uuid),
        path,
        reference="test",
        replace=True,
        interactive=False,
    )
    upload = library.uploads.last()

    assert upload.import_reference == "test"

    mocked_process.assert_called_once_with(upload_id=upload.pk)


def test_import_files_skip_if_path_already_imported(factories, mocker):
    library = factories["music.Library"](actor__local=True)
    path = os.path.join(DATA_DIR, "dummy_file.ogg")

    # existing one with same source
    factories["music.Upload"](
        library=library, import_status="finished", source="file://{}".format(path)
    )

    call_command(
        "import_files", str(library.uuid), path, async=False, interactive=False
    )
    assert library.uploads.count() == 1


def test_import_files_in_place(factories, mocker, settings):
    settings.MUSIC_DIRECTORY_PATH = DATA_DIR
    mocked_process = mocker.patch("funkwhale_api.music.tasks.process_upload")
    library = factories["music.Library"](actor__local=True)
    path = os.path.join(DATA_DIR, "utf8-éà◌.ogg")
    call_command(
        "import_files",
        str(library.uuid),
        path,
        async_=False,
        in_place=True,
        interactive=False,
    )
    upload = library.uploads.last()
    assert bool(upload.audio_file) is False
    mocked_process.assert_called_once_with(upload_id=upload.pk)


def test_storage_rename_utf_8_files(factories):
    upload = factories["music.Upload"](audio_file__filename="été.ogg")
    assert upload.audio_file.name.endswith("ete.ogg")
