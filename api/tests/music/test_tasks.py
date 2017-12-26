from funkwhale_api.providers.acoustid import get_acoustid_client

from funkwhale_api.music import tasks


def test_set_acoustid_on_track_file(factories, mocker):
    track_file = factories['music.TrackFile'](acoustid_track_id=None)
    id = 'e475bf79-c1ce-4441-bed7-1e33f226c0a2'
    payload = {
        'results': [
            {'id': id,
             'recordings': [
                {'artists': [
                    {'id': '9c6bddde-6228-4d9f-ad0d-03f6fcb19e13',
                     'name': 'Binärpilot'}],
                 'duration': 268,
                 'id': 'f269d497-1cc0-4ae4-a0c4-157ec7d73fcb',
                 'title': 'Bend'}],
            'score': 0.860825}],
        'status': 'ok'
    }
    m = mocker.patch('acoustid.match', return_value=payload)
    r = tasks.set_acoustid_on_track_file(track_file_id=track_file.pk)
    track_file.refresh_from_db()

    assert str(track_file.acoustid_track_id) == id
    assert r == id
    m.assert_called_once_with('', track_file.audio_file.path, parse=False)


def test_set_acoustid_on_track_file_required_high_score(factories, mocker):
    track_file = factories['music.TrackFile'](acoustid_track_id=None)
    id = 'e475bf79-c1ce-4441-bed7-1e33f226c0a2'
    payload = {
        'results': [{'score': 0.79}],
        'status': 'ok'
    }
    m = mocker.patch('acoustid.match', return_value=payload)
    r = tasks.set_acoustid_on_track_file(track_file_id=track_file.pk)
    track_file.refresh_from_db()

    assert track_file.acoustid_track_id is None
