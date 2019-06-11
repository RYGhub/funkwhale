import pytest

from funkwhale_api.common import storage


@pytest.mark.parametrize(
    "filename, expected",
    [("집으로 가는 길.mp3", "jibeuro-ganeun-gil.mp3"), ("éàe*$i$.ogg", "eaei.ogg")],
)
def test_asciionly(filename, expected):
    assert storage.asciionly(filename) == expected


@pytest.mark.parametrize(
    "storage_class, parent_class",
    [
        (storage.ASCIIFileSystemStorage, storage.FileSystemStorage),
        (storage.ASCIIS3Boto3Storage, storage.S3Boto3Storage),
    ],
)
def test_ascii_storage_call_asciionly(storage_class, parent_class, mocker):
    """Cf #847"""
    asciionly = mocker.patch.object(storage, "asciionly")
    parent_get_valid_filename = mocker.patch.object(parent_class, "get_valid_name")
    st = storage_class()
    assert st.get_valid_name("test") == parent_get_valid_filename.return_value
    asciionly.assert_called_once_with("test")
    parent_get_valid_filename.assert_called_once_with(asciionly.return_value)
