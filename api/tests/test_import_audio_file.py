import os

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from funkwhale_api.music.models import ImportJob

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")


@pytest.mark.skip("XXX : wip")
def test_management_command_requires_a_valid_username(factories, mocker):
    path = os.path.join(DATA_DIR, "dummy_file.ogg")
    factories["users.User"](username="me")
    mocker.patch(
        "funkwhale_api.providers.audiofile.management.commands.import_files.Command.do_import",  # noqa
        return_value=(mocker.MagicMock(), []),
    )
    with pytest.raises(CommandError):
        call_command("import_files", path, username="not_me", interactive=False)
    call_command("import_files", path, username="me", interactive=False)


def test_in_place_import_only_from_music_dir(factories, settings):
    factories["users.User"](username="me")
    settings.MUSIC_DIRECTORY_PATH = "/nope"
    path = os.path.join(DATA_DIR, "dummy_file.ogg")
    with pytest.raises(CommandError):
        call_command(
            "import_files", path, in_place=True, username="me", interactive=False
        )


@pytest.mark.skip("XXX : wip")
def test_import_with_multiple_argument(factories, mocker):
    factories["users.User"](username="me")
    path1 = os.path.join(DATA_DIR, "dummy_file.ogg")
    path2 = os.path.join(DATA_DIR, "utf8-éà◌.ogg")
    mocked_filter = mocker.patch(
        "funkwhale_api.providers.audiofile.management.commands.import_files.Command.filter_matching",
        return_value=({"new": [], "skipped": []}),
    )
    call_command("import_files", path1, path2, username="me", interactive=False)
    mocked_filter.assert_called_once_with([path1, path2])


@pytest.mark.skip("Refactoring in progress")
def test_import_with_replace_flag(factories, mocker):
    factories["users.User"](username="me")
    path = os.path.join(DATA_DIR, "dummy_file.ogg")
    mocked_job_run = mocker.patch("funkwhale_api.music.tasks.import_job_run")
    call_command("import_files", path, username="me", replace=True, interactive=False)
    created_job = ImportJob.objects.latest("id")

    assert created_job.replace_if_duplicate is True
    mocked_job_run.assert_called_once_with(
        import_job_id=created_job.id, use_acoustid=False
    )


@pytest.mark.skip("Refactoring in progress")
def test_import_files_creates_a_batch_and_job(factories, mocker):
    m = mocker.patch("funkwhale_api.music.tasks.import_job_run")
    user = factories["users.User"](username="me")
    path = os.path.join(DATA_DIR, "dummy_file.ogg")
    call_command("import_files", path, username="me", async=False, interactive=False)

    batch = user.imports.latest("id")
    assert batch.source == "shell"
    assert batch.jobs.count() == 1

    job = batch.jobs.first()

    assert job.status == "pending"
    with open(path, "rb") as f:
        assert job.audio_file.read() == f.read()

    assert job.source == "file://" + path
    m.assert_called_once_with(import_job_id=job.pk, use_acoustid=False)


@pytest.mark.skip("XXX : wip")
def test_import_files_skip_if_path_already_imported(factories, mocker):
    user = factories["users.User"](username="me")
    path = os.path.join(DATA_DIR, "dummy_file.ogg")
    factories["music.Upload"](source="file://{}".format(path))

    call_command("import_files", path, username="me", async=False, interactive=False)
    assert user.imports.count() == 0


@pytest.mark.skip("Refactoring in progress")
def test_import_files_works_with_utf8_file_name(factories, mocker):
    m = mocker.patch("funkwhale_api.music.tasks.import_job_run")
    user = factories["users.User"](username="me")
    path = os.path.join(DATA_DIR, "utf8-éà◌.ogg")
    call_command("import_files", path, username="me", async=False, interactive=False)
    batch = user.imports.latest("id")
    job = batch.jobs.first()
    m.assert_called_once_with(import_job_id=job.pk, use_acoustid=False)


@pytest.mark.skip("Refactoring in progress")
def test_import_files_in_place(factories, mocker, settings):
    settings.MUSIC_DIRECTORY_PATH = DATA_DIR
    m = mocker.patch("funkwhale_api.music.tasks.import_job_run")
    user = factories["users.User"](username="me")
    path = os.path.join(DATA_DIR, "utf8-éà◌.ogg")
    call_command(
        "import_files",
        path,
        username="me",
        async=False,
        in_place=True,
        interactive=False,
    )
    batch = user.imports.latest("id")
    job = batch.jobs.first()
    assert bool(job.audio_file) is False
    m.assert_called_once_with(import_job_id=job.pk, use_acoustid=False)


def test_storage_rename_utf_8_files(factories):
    upload = factories["music.Upload"](audio_file__filename="été.ogg")
    assert upload.audio_file.name.endswith("ete.ogg")
