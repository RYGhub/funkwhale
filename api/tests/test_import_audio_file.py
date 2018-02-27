import pytest
import acoustid
import datetime
import os
from django.core.management import call_command
from django.core.management.base import CommandError

from funkwhale_api.providers.audiofile import tasks
from funkwhale_api.music import tasks as music_tasks

DATA_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'files'
)


def test_can_create_track_from_file_metadata(db, mocker):
    mocker.patch('acoustid.match', side_effect=acoustid.WebServiceError('test'))
    metadata = {
        'artist': ['Test artist'],
        'album': ['Test album'],
        'title': ['Test track'],
        'TRACKNUMBER': ['4'],
        'date': ['2012-08-15'],
        'musicbrainz_albumid': ['a766da8b-8336-47aa-a3ee-371cc41ccc75'],
        'musicbrainz_trackid': ['bd21ac48-46d8-4e78-925f-d9cc2a294656'],
        'musicbrainz_artistid': ['013c8e5b-d72a-4cd3-8dee-6c64d6125823'],
    }
    m1 = mocker.patch('mutagen.File', return_value=metadata)
    m2 = mocker.patch(
        'funkwhale_api.music.metadata.Metadata.get_file_type',
        return_value='OggVorbis',
    )
    track = tasks.import_track_data_from_path(
        os.path.join(DATA_DIR, 'dummy_file.ogg'))

    assert track.title == metadata['title'][0]
    assert track.mbid == metadata['musicbrainz_trackid'][0]
    assert track.position == 4
    assert track.album.title == metadata['album'][0]
    assert track.album.mbid == metadata['musicbrainz_albumid'][0]
    assert track.album.release_date == datetime.date(2012, 8, 15)
    assert track.artist.name == metadata['artist'][0]
    assert track.artist.mbid == metadata['musicbrainz_artistid'][0]


def test_management_command_requires_a_valid_username(factories, mocker):
    path = os.path.join(DATA_DIR, 'dummy_file.ogg')
    user = factories['users.User'](username='me')
    mocker.patch('funkwhale_api.providers.audiofile.management.commands.import_files.Command.do_import')  # NOQA
    with pytest.raises(CommandError):
        call_command('import_files', path, username='not_me', interactive=False)
    call_command('import_files', path, username='me', interactive=False)


def test_import_files_creates_a_batch_and_job(factories, mocker):
    m = m = mocker.patch('funkwhale_api.common.utils.on_commit')
    user = factories['users.User'](username='me')
    path = os.path.join(DATA_DIR, 'dummy_file.ogg')
    call_command(
        'import_files',
        path,
        username='me',
        async=True,
        interactive=False)

    batch = user.imports.latest('id')
    assert batch.source == 'shell'
    assert batch.jobs.count() == 1

    job = batch.jobs.first()

    assert job.status == 'pending'
    with open(path, 'rb') as f:
        assert job.audio_file.read() == f.read()

    assert job.source == 'file://' + path
    m.assert_called_once_with(
        music_tasks.import_job_run.delay,
        import_job_id=job.pk)
