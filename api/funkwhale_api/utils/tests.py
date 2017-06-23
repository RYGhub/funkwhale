import tempfile
import shutil


class TMPDirTestCaseMixin(object):
    def setUp(self):
        super().tearDown()
        self.download_dir = tempfile.mkdtemp()

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.download_dir)
