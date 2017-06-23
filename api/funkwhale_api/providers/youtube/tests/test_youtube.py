import json
from collections import OrderedDict
import unittest
from test_plus.test import TestCase
from django.core.urlresolvers import reverse
from funkwhale_api.providers.youtube.client import client

from . import data as api_data

class TestAPI(TestCase):

    @unittest.mock.patch(
        'funkwhale_api.providers.youtube.client._do_search',
        return_value=api_data.search['8 bit adventure'])
    def test_can_get_search_results_from_youtube(self, *mocks):
        query = '8 bit adventure'

        results = client.search(query)
        self.assertEqual(results[0]['id']['videoId'], '0HxZn6CzOIo')
        self.assertEqual(results[0]['snippet']['title'], 'AdhesiveWombat - 8 Bit Adventure')
        self.assertEqual(results[0]['full_url'], 'https://www.youtube.com/watch?v=0HxZn6CzOIo')

    @unittest.mock.patch(
        'funkwhale_api.providers.youtube.client._do_search',
        return_value=api_data.search['8 bit adventure'])
    def test_can_get_search_results_from_funkwhale(self, *mocks):
        query = '8 bit adventure'
        expected = json.dumps(client.search(query))
        url = self.reverse('api:providers:youtube:search')
        response = self.client.get(url + '?query={0}'.format(query))

        self.assertJSONEqual(expected, json.loads(response.content.decode('utf-8')))

    @unittest.mock.patch(
        'funkwhale_api.providers.youtube.client._do_search',
        side_effect=[
            api_data.search['8 bit adventure'],
            api_data.search['system of a down toxicity'],
        ]
    )
    def test_can_send_multiple_queries_at_once(self, *mocks):
        queries = OrderedDict()
        queries['1'] = {
            'q': '8 bit adventure',
        }
        queries['2'] = {
            'q': 'system of a down toxicity',
        }

        results = client.search_multiple(queries)

        self.assertEqual(results['1'][0]['id']['videoId'], '0HxZn6CzOIo')
        self.assertEqual(results['1'][0]['snippet']['title'], 'AdhesiveWombat - 8 Bit Adventure')
        self.assertEqual(results['1'][0]['full_url'], 'https://www.youtube.com/watch?v=0HxZn6CzOIo')
        self.assertEqual(results['2'][0]['id']['videoId'], 'BorYwGi2SJc')
        self.assertEqual(results['2'][0]['snippet']['title'], 'System of a Down: Toxicity')
        self.assertEqual(results['2'][0]['full_url'], 'https://www.youtube.com/watch?v=BorYwGi2SJc')

    @unittest.mock.patch(
        'funkwhale_api.providers.youtube.client._do_search',
        return_value=api_data.search['8 bit adventure'],
    )
    def test_can_send_multiple_queries_at_once_from_funwkhale(self, *mocks):
        queries = OrderedDict()
        queries['1'] = {
            'q': '8 bit adventure',
        }

        expected = json.dumps(client.search_multiple(queries))
        url = self.reverse('api:providers:youtube:searchs')
        response = self.client.post(
            url, json.dumps(queries), content_type='application/json')

        self.assertJSONEqual(expected, json.loads(response.content.decode('utf-8')))
