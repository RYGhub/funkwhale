import os

from funkwhale_api import downloader


def test_can_download_audio_from_youtube_url_to_vorbis(tmpdir):
    data = downloader.download(
        'https://www.youtube.com/watch?v=tPEE9ZwTmy0',
        target_directory=tmpdir)
    assert data['audio_file_path'] == os.path.join(tmpdir, 'tPEE9ZwTmy0.ogg')
    assert os.path.exists(data['audio_file_path'])
