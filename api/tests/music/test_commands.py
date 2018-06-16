import os

from funkwhale_api.music.management.commands import fix_track_files

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def test_fix_track_files_bitrate_length(factories, mocker):
    tf1 = factories["music.TrackFile"](bitrate=1, duration=2)
    tf2 = factories["music.TrackFile"](bitrate=None, duration=None)
    c = fix_track_files.Command()

    mocker.patch(
        "funkwhale_api.music.utils.get_audio_file_data",
        return_value={"bitrate": 42, "length": 43},
    )

    c.fix_file_data(dry_run=False)

    tf1.refresh_from_db()
    tf2.refresh_from_db()

    # not updated
    assert tf1.bitrate == 1
    assert tf1.duration == 2

    # updated
    assert tf2.bitrate == 42
    assert tf2.duration == 43


def test_fix_track_files_size(factories, mocker):
    tf1 = factories["music.TrackFile"](size=1)
    tf2 = factories["music.TrackFile"](size=None)
    c = fix_track_files.Command()

    mocker.patch("funkwhale_api.music.models.TrackFile.get_file_size", return_value=2)

    c.fix_file_size(dry_run=False)

    tf1.refresh_from_db()
    tf2.refresh_from_db()

    # not updated
    assert tf1.size == 1

    # updated
    assert tf2.size == 2


def test_fix_track_files_mimetype(factories, mocker):
    mp3_path = os.path.join(DATA_DIR, "test.mp3")
    ogg_path = os.path.join(DATA_DIR, "test.ogg")
    tf1 = factories["music.TrackFile"](
        audio_file__from_path=mp3_path,
        source="file://{}".format(mp3_path),
        mimetype="application/x-empty",
    )

    # this one already has a mimetype set, to it should not be updated
    tf2 = factories["music.TrackFile"](
        audio_file__from_path=ogg_path,
        source="file://{}".format(ogg_path),
        mimetype="audio/something",
    )
    c = fix_track_files.Command()
    c.fix_mimetypes(dry_run=False)

    tf1.refresh_from_db()
    tf2.refresh_from_db()

    assert tf1.mimetype == "audio/mpeg"
    assert tf2.mimetype == "audio/something"
