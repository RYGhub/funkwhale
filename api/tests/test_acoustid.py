from funkwhale_api.providers.acoustid import get_acoustid_client


def test_client_is_configured_with_correct_api_key(preferences):
    api_key = 'hello world'
    preferences['providers_acoustid__api_key'] = api_key

    client = get_acoustid_client()
    assert client.api_key == api_key


def test_client_returns_raw_results(db, mocker, preferences):
    api_key = 'test'
    preferences['providers_acoustid__api_key'] = api_key
    payload = {
        'results': [
            {'id': 'e475bf79-c1ce-4441-bed7-1e33f226c0a2',
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
    client = get_acoustid_client()
    response = client.match('/tmp/noopfile.mp3')

    assert response == payload
    m.assert_called_once_with('test', '/tmp/noopfile.mp3', parse=False)
