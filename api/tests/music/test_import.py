import json

from django.urls import reverse

from . import data as api_data


def test_create_import_can_bind_to_request(
        mocker, factories, superuser_api_client):
    request = factories['requests.ImportRequest']()

    mocker.patch('funkwhale_api.music.tasks.import_job_run')
    mocker.patch(
        'funkwhale_api.musicbrainz.api.artists.get',
        return_value=api_data.artists['get']['soad'])
    mocker.patch(
        'funkwhale_api.musicbrainz.api.images.get_front',
        return_value=b'')
    mocker.patch(
        'funkwhale_api.musicbrainz.api.releases.get',
        return_value=api_data.albums['get_with_includes']['hypnotize'])
    payload = {
        'releaseId': '47ae093f-1607-49a3-be11-a15d335ccc94',
        'importRequest': request.pk,
        'tracks': [
            {
                'mbid': '1968a9d6-8d92-4051-8f76-674e157b6eed',
                'source': 'https://www.youtube.com/watch?v=1111111111',
            }
        ]
    }
    url = reverse('api:v1:submit-album')
    response = superuser_api_client.post(
        url, json.dumps(payload), content_type='application/json')
    batch = request.import_batches.latest('id')

    assert batch.import_request == request
