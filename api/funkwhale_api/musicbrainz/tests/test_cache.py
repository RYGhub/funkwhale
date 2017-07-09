import unittest
from test_plus.test import TestCase

from funkwhale_api.musicbrainz import client


class TestAPI(TestCase):
    def test_can_search_recording_in_musicbrainz_api(self, *mocks):
        r = {'hello': 'world'}
        mocked = 'funkwhale_api.musicbrainz.client._api.search_artists'
        with unittest.mock.patch(mocked, return_value=r) as m:
            self.assertEqual(client.api.artists.search('test'), r)
            # now call from cache
            self.assertEqual(client.api.artists.search('test'), r)
            self.assertEqual(client.api.artists.search('test'), r)

            self.assertEqual(m.call_count, 1)
