import os
from test_plus.test import TestCase
from .. import downloader
from funkwhale_api.utils.tests import TMPDirTestCaseMixin


class TestDownloader(TMPDirTestCaseMixin, TestCase):

    def test_can_download_audio_from_youtube_url_to_vorbis(self):
        data = downloader.download('https://www.youtube.com/watch?v=tPEE9ZwTmy0', target_directory=self.download_dir)
        self.assertEqual(
            data['audio_file_path'],
            os.path.join(self.download_dir, 'tPEE9ZwTmy0.ogg'))
        self.assertTrue(os.path.exists(data['audio_file_path']))
