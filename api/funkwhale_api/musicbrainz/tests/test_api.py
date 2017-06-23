import json
import unittest
from test_plus.test import TestCase
from django.core.urlresolvers import reverse

from funkwhale_api.musicbrainz import api
from . import data as api_data


class TestAPI(TestCase):
    @unittest.mock.patch(
        'funkwhale_api.musicbrainz.api.recordings.search',
        return_value=api_data.recordings['search']['brontide matador'])
    def test_can_search_recording_in_musicbrainz_api(self, *mocks):
        query = 'brontide matador'
        url = reverse('api:providers:musicbrainz:search-recordings')
        expected = api_data.recordings['search']['brontide matador']
        response = self.client.get(url, data={'query': query})

        self.assertEqual(expected, json.loads(response.content.decode('utf-8')))

    @unittest.mock.patch(
        'funkwhale_api.musicbrainz.api.releases.search',
        return_value=api_data.releases['search']['brontide matador'])
    def test_can_search_release_in_musicbrainz_api(self, *mocks):
        query = 'brontide matador'
        url = reverse('api:providers:musicbrainz:search-releases')
        expected = api_data.releases['search']['brontide matador']
        response = self.client.get(url, data={'query': query})

        self.assertEqual(expected, json.loads(response.content.decode('utf-8')))

    @unittest.mock.patch(
        'funkwhale_api.musicbrainz.api.artists.search',
        return_value=api_data.artists['search']['lost fingers'])
    def test_can_search_artists_in_musicbrainz_api(self, *mocks):
        query = 'lost fingers'
        url = reverse('api:providers:musicbrainz:search-artists')
        expected = api_data.artists['search']['lost fingers']
        response = self.client.get(url, data={'query': query})

        self.assertEqual(expected, json.loads(response.content.decode('utf-8')))

    @unittest.mock.patch(
        'funkwhale_api.musicbrainz.api.artists.get',
        return_value=api_data.artists['get']['lost fingers'])
    def test_can_get_artist_in_musicbrainz_api(self, *mocks):
        uuid = 'ac16bbc0-aded-4477-a3c3-1d81693d58c9'
        url = reverse('api:providers:musicbrainz:artist-detail', kwargs={
            'uuid': uuid,
        })
        response = self.client.get(url)
        expected = api_data.artists['get']['lost fingers']

        self.assertEqual(expected, json.loads(response.content.decode('utf-8')))

    @unittest.mock.patch(
        'funkwhale_api.musicbrainz.api.release_groups.browse',
        return_value=api_data.release_groups['browse']['lost fingers'])
    def test_can_broswe_release_group_using_musicbrainz_api(self, *mocks):
        uuid = 'ac16bbc0-aded-4477-a3c3-1d81693d58c9'
        url = reverse(
            'api:providers:musicbrainz:release-group-browse',
            kwargs={
                'artist_uuid': uuid,
            }
        )
        response = self.client.get(url)
        expected = api_data.release_groups['browse']['lost fingers']

        self.assertEqual(expected, json.loads(response.content.decode('utf-8')))

    @unittest.mock.patch(
        'funkwhale_api.musicbrainz.api.releases.browse',
        return_value=api_data.releases['browse']['Lost in the 80s'])
    def test_can_broswe_releases_using_musicbrainz_api(self, *mocks):
        uuid = 'f04ed607-11b7-3843-957e-503ecdd485d1'
        url = reverse(
            'api:providers:musicbrainz:release-browse',
            kwargs={
                'release_group_uuid': uuid,
            }
        )
        response = self.client.get(url)
        expected = api_data.releases['browse']['Lost in the 80s']

        self.assertEqual(expected, json.loads(response.content.decode('utf-8')))
