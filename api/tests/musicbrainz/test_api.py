import json
from django.urls import reverse

from funkwhale_api.musicbrainz import api



def test_can_search_recording_in_musicbrainz_api(
        recordings, db, mocker, logged_in_api_client):
    mocker.patch(
        'funkwhale_api.musicbrainz.api.recordings.search',
        return_value=recordings['search']['brontide matador'])
    query = 'brontide matador'
    url = reverse('api:v1:providers:musicbrainz:search-recordings')
    expected = recordings['search']['brontide matador']
    response = logged_in_api_client.get(url, data={'query': query})

    assert expected == response.data


def test_can_search_release_in_musicbrainz_api(releases, db, mocker, logged_in_api_client):
    mocker.patch(
        'funkwhale_api.musicbrainz.api.releases.search',
        return_value=releases['search']['brontide matador'])
    query = 'brontide matador'
    url = reverse('api:v1:providers:musicbrainz:search-releases')
    expected = releases['search']['brontide matador']
    response = logged_in_api_client.get(url, data={'query': query})

    assert expected == response.data


def test_can_search_artists_in_musicbrainz_api(artists, db, mocker, logged_in_api_client):
    mocker.patch(
        'funkwhale_api.musicbrainz.api.artists.search',
        return_value=artists['search']['lost fingers'])
    query = 'lost fingers'
    url = reverse('api:v1:providers:musicbrainz:search-artists')
    expected = artists['search']['lost fingers']
    response = logged_in_api_client.get(url, data={'query': query})

    assert expected == response.data


def test_can_get_artist_in_musicbrainz_api(artists, db, mocker, logged_in_api_client):
    mocker.patch(
        'funkwhale_api.musicbrainz.api.artists.get',
        return_value=artists['get']['lost fingers'])
    uuid = 'ac16bbc0-aded-4477-a3c3-1d81693d58c9'
    url = reverse('api:v1:providers:musicbrainz:artist-detail', kwargs={
        'uuid': uuid,
    })
    response = logged_in_api_client.get(url)
    expected = artists['get']['lost fingers']

    assert expected == response.data


def test_can_broswe_release_group_using_musicbrainz_api(
        release_groups, db, mocker, logged_in_api_client):
    mocker.patch(
        'funkwhale_api.musicbrainz.api.release_groups.browse',
        return_value=release_groups['browse']['lost fingers'])
    uuid = 'ac16bbc0-aded-4477-a3c3-1d81693d58c9'
    url = reverse(
        'api:v1:providers:musicbrainz:release-group-browse',
        kwargs={
            'artist_uuid': uuid,
        }
    )
    response = logged_in_api_client.get(url)
    expected = release_groups['browse']['lost fingers']

    assert expected == response.data


def test_can_broswe_releases_using_musicbrainz_api(
        releases, db, mocker, logged_in_api_client):
    mocker.patch(
        'funkwhale_api.musicbrainz.api.releases.browse',
        return_value=releases['browse']['Lost in the 80s'])
    uuid = 'f04ed607-11b7-3843-957e-503ecdd485d1'
    url = reverse(
        'api:v1:providers:musicbrainz:release-browse',
        kwargs={
            'release_group_uuid': uuid,
        }
    )
    response = logged_in_api_client.get(url)
    expected = releases['browse']['Lost in the 80s']

    assert expected == response.data
