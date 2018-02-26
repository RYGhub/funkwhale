from funkwhale_api.music import utils


def test_guess_mimetype_try_using_extension(factories, mocker):
    mocker.patch(
        'magic.from_buffer', return_value='audio/mpeg')
    f = factories['music.TrackFile'].build(
        audio_file__filename='test.ogg')

    assert utils.guess_mimetype(f.audio_file) == 'audio/mpeg'


def test_guess_mimetype_try_using_extension_if_fail(factories, mocker):
    mocker.patch(
        'magic.from_buffer', return_value='application/octet-stream')
    f = factories['music.TrackFile'].build(
        audio_file__filename='test.mp3')

    assert utils.guess_mimetype(f.audio_file) == 'audio/mpeg'
