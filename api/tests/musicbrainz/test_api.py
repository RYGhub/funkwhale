import json
from django.urls import reverse

from funkwhale_api.musicbrainz import api
from . import data as api_data



def test_can_search_recording_in_musicbrainz_api(db, mocker, client):
    mocker.patch(
        'funkwhale_api.musicbrainz.api.recordings.search',
        return_value=api_data.recordings['search']['brontide matador'])
    query = 'brontide matador'
    url = reverse('api:v1:providers:musicbrainz:search-recordings')
    expected = api_data.recordings['search']['brontide matador']
    response = client.get(url, data={'query': query})

    assert expected == json.loads(response.content.decode('utf-8'))


def test_can_search_release_in_musicbrainz_api(db, mocker, client):
    mocker.patch(
        'funkwhale_api.musicbrainz.api.releases.search',
        return_value=api_data.releases['search']['brontide matador'])
    query = 'brontide matador'
    url = reverse('api:v1:providers:musicbrainz:search-releases')
    expected = api_data.releases['search']['brontide matador']
    response = client.get(url, data={'query': query})

    assert expected == json.loads(response.content.decode('utf-8'))


def test_can_search_artists_in_musicbrainz_api(db, mocker, client):
    mocker.patch(
        'funkwhale_api.musicbrainz.api.artists.search',
        return_value=api_data.artists['search']['lost fingers'])
    query = 'lost fingers'
    url = reverse('api:v1:providers:musicbrainz:search-artists')
    expected = api_data.artists['search']['lost fingers']
    response = client.get(url, data={'query': query})

    assert expected == json.loads(response.content.decode('utf-8'))


def test_can_get_artist_in_musicbrainz_api(db, mocker, client):
    mocker.patch(
        'funkwhale_api.musicbrainz.api.artists.get',
        return_value=api_data.artists['get']['lost fingers'])
    uuid = 'ac16bbc0-aded-4477-a3c3-1d81693d58c9'
    url = reverse('api:v1:providers:musicbrainz:artist-detail', kwargs={
        'uuid': uuid,
    })
    response = client.get(url)
    expected = api_data.artists['get']['lost fingers']

    assert expected == json.loads(response.content.decode('utf-8'))


def test_can_broswe_release_group_using_musicbrainz_api(db, mocker, client):
    mocker.patch(
        'funkwhale_api.musicbrainz.api.release_groups.browse',
        return_value=api_data.release_groups['browse']['lost fingers'])
    uuid = 'ac16bbc0-aded-4477-a3c3-1d81693d58c9'
    url = reverse(
        'api:v1:providers:musicbrainz:release-group-browse',
        kwargs={
            'artist_uuid': uuid,
        }
    )
    response = client.get(url)
    expected = api_data.release_groups['browse']['lost fingers']

    assert expected == json.loads(response.content.decode('utf-8'))


def test_can_broswe_releases_using_musicbrainz_api(db, mocker, client):
    mocker.patch(
        'funkwhale_api.musicbrainz.api.releases.browse',
        return_value=api_data.releases['browse']['Lost in the 80s'])
    uuid = 'f04ed607-11b7-3843-957e-503ecdd485d1'
    url = reverse(
        'api:v1:providers:musicbrainz:release-browse',
        kwargs={
            'release_group_uuid': uuid,
        }
    )
    response = client.get(url)
    expected = api_data.releases['browse']['Lost in the 80s']

    assert expected == json.loads(response.content.decode('utf-8'))
