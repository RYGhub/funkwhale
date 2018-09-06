import os
import pytest
import uuid

from django import forms

from funkwhale_api.music import importers
from funkwhale_api.music import models

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def test_importer_cleans():
    importer = importers.Importer(models.Artist)
    with pytest.raises(forms.ValidationError):
        importer.load({"name": "", "mbid": uuid.uuid4()}, {}, [])
