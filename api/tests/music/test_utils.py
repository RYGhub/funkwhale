import os

import pytest

from funkwhale_api.music import utils

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def test_guess_mimetype_try_using_extension(factories, mocker):
    mocker.patch("magic.from_buffer", return_value="audio/mpeg")
    f = factories["music.Upload"].build(audio_file__filename="test.ogg")

    assert utils.guess_mimetype(f.audio_file) == "audio/mpeg"


@pytest.mark.parametrize("wrong", ["application/octet-stream", "application/x-empty"])
def test_guess_mimetype_try_using_extension_if_fail(wrong, factories, mocker):
    mocker.patch("magic.from_buffer", return_value=wrong)
    f = factories["music.Upload"].build(audio_file__filename="test.mp3")

    assert utils.guess_mimetype(f.audio_file) == "audio/mpeg"


@pytest.mark.parametrize(
    "name, expected",
    [
        ("sample.flac", {"bitrate": 1608000, "length": 0.001}),
        ("test.mp3", {"bitrate": 8000, "length": 267.70285714285717}),
        ("test.ogg", {"bitrate": 112000, "length": 1}),
    ],
)
def test_get_audio_file_data(name, expected):
    path = os.path.join(DATA_DIR, name)
    with open(path, "rb") as f:
        result = utils.get_audio_file_data(f)

    assert result == expected


def test_guess_mimetype_dont_crash_with_s3(factories, mocker, settings):
    """See #857"""
    settings.DEFAULT_FILE_STORAGE = "funkwhale_api.common.storage.ASCIIS3Boto3Storage"
    mocker.patch("magic.from_buffer", return_value="none")
    f = factories["music.Upload"].build(audio_file__filename="test.mp3")

    assert utils.guess_mimetype(f.audio_file) == "audio/mpeg"


def test_increment_downloads_count(factories, mocker, cache, anonymous_user, settings):
    ident = {"type": "anonymous", "id": "noop"}
    get_ident = mocker.patch(
        "funkwhale_api.common.throttling.get_ident", return_value=ident
    )
    cache_set = mocker.spy(utils.cache, "set")
    wsgi_request = mocker.Mock(META={})
    upload = factories["music.Upload"]()
    utils.increment_downloads_count(
        upload=upload, user=anonymous_user, wsgi_request=wsgi_request
    )

    upload.refresh_from_db()
    get_ident.assert_called_once_with(user=anonymous_user, request=wsgi_request)

    assert upload.downloads_count == 1
    assert upload.track.downloads_count == 1
    cache_set.assert_called_once_with(
        "downloads_count:upload-{}:{}-{}".format(upload.pk, ident["type"], ident["id"]),
        1,
        settings.MIN_DELAY_BETWEEN_DOWNLOADS_COUNT,
    )


def test_increment_downloads_count_already_tracked(
    factories, mocker, cache, anonymous_user
):
    ident = {"type": "anonymous", "id": "noop"}
    mocker.patch("funkwhale_api.common.throttling.get_ident", return_value=ident)
    wsgi_request = mocker.Mock(META={})
    upload = factories["music.Upload"]()
    cache.set(
        "downloads_count:upload-{}:{}-{}".format(upload.pk, ident["type"], ident["id"]),
        1,
    )

    utils.increment_downloads_count(
        upload=upload, user=anonymous_user, wsgi_request=wsgi_request
    )

    upload.refresh_from_db()

    assert upload.downloads_count == 0
    assert upload.track.downloads_count == 0
