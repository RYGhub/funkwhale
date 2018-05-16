from funkwhale_api.music.management.commands import fix_track_files


def test_fix_track_files_bitrate_length(factories, mocker):
    tf1 = factories['music.TrackFile'](bitrate=1, duration=2)
    tf2 = factories['music.TrackFile'](bitrate=None, duration=None)
    c = fix_track_files.Command()

    mocker.patch(
        'funkwhale_api.music.utils.get_audio_file_data',
        return_value={'bitrate': 42, 'length': 43})

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
    tf1 = factories['music.TrackFile'](size=1)
    tf2 = factories['music.TrackFile'](size=None)
    c = fix_track_files.Command()

    mocker.patch(
        'funkwhale_api.music.models.TrackFile.get_file_size',
        return_value=2)

    c.fix_file_size(dry_run=False)

    tf1.refresh_from_db()
    tf2.refresh_from_db()

    # not updated
    assert tf1.size == 1

    # updated
    assert tf2.size == 2
