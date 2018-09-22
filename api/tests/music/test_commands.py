import os

from funkwhale_api.music.management.commands import fix_uploads

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def test_fix_uploads_bitrate_length(factories, mocker):
    upload1 = factories["music.Upload"](bitrate=1, duration=2)
    upload2 = factories["music.Upload"](bitrate=None, duration=None)
    c = fix_uploads.Command()

    mocker.patch(
        "funkwhale_api.music.utils.get_audio_file_data",
        return_value={"bitrate": 42, "length": 43},
    )

    c.fix_file_data(dry_run=False)

    upload1.refresh_from_db()
    upload2.refresh_from_db()

    # not updated
    assert upload1.bitrate == 1
    assert upload1.duration == 2

    # updated
    assert upload2.bitrate == 42
    assert upload2.duration == 43


def test_fix_uploads_size(factories, mocker):
    upload1 = factories["music.Upload"]()
    upload2 = factories["music.Upload"]()
    upload1.__class__.objects.filter(pk=upload1.pk).update(size=1)
    upload2.__class__.objects.filter(pk=upload2.pk).update(size=None)
    c = fix_uploads.Command()

    mocker.patch("funkwhale_api.music.models.Upload.get_file_size", return_value=2)

    c.fix_file_size(dry_run=False)

    upload1.refresh_from_db()
    upload2.refresh_from_db()

    # not updated
    assert upload1.size == 1

    # updated
    assert upload2.size == 2


def test_fix_uploads_mimetype(factories, mocker):
    mp3_path = os.path.join(DATA_DIR, "test.mp3")
    ogg_path = os.path.join(DATA_DIR, "test.ogg")
    upload1 = factories["music.Upload"](
        audio_file__from_path=mp3_path,
        source="file://{}".format(mp3_path),
        mimetype="application/x-empty",
    )

    # this one already has a mimetype set, to it should not be updated
    upload2 = factories["music.Upload"](
        audio_file__from_path=ogg_path,
        source="file://{}".format(ogg_path),
        mimetype="audio/something",
    )
    c = fix_uploads.Command()
    c.fix_mimetypes(dry_run=False)

    upload1.refresh_from_db()
    upload2.refresh_from_db()

    assert upload1.mimetype == "audio/mpeg"
    assert upload2.mimetype == "audio/something"
