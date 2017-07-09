import json
from collections import OrderedDict
import unittest
from test_plus.test import TestCase
from django.core.urlresolvers import reverse
from funkwhale_api.providers.youtube.client import client

from . import data as api_data

class TestAPI(TestCase):
    maxDiff = None
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
        url = self.reverse('api:v1:providers:youtube:search')
        response = self.client.get(url + '?query={0}'.format(query))
        # we should cast the youtube result to something more generic
        expected = {
            "id": "0HxZn6CzOIo",
            "url": "https://www.youtube.com/watch?v=0HxZn6CzOIo",
            "type": "youtube#video",
            "description": "Make sure to apply adhesive evenly before use. GET IT HERE: http://adhesivewombat.bandcamp.com/album/marsupial-madness Facebook: ...",
            "channelId": "UCps63j3krzAG4OyXeEyuhFw",
            "title": "AdhesiveWombat - 8 Bit Adventure",
            "channelTitle": "AdhesiveWombat",
            "publishedAt": "2012-08-22T18:41:03.000Z",
            "cover": "https://i.ytimg.com/vi/0HxZn6CzOIo/hqdefault.jpg"
        }

        self.assertEqual(
            json.loads(response.content.decode('utf-8'))[0], expected)

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

        expected = {
            "id": "0HxZn6CzOIo",
            "url": "https://www.youtube.com/watch?v=0HxZn6CzOIo",
            "type": "youtube#video",
            "description": "Make sure to apply adhesive evenly before use. GET IT HERE: http://adhesivewombat.bandcamp.com/album/marsupial-madness Facebook: ...",
            "channelId": "UCps63j3krzAG4OyXeEyuhFw",
            "title": "AdhesiveWombat - 8 Bit Adventure",
            "channelTitle": "AdhesiveWombat",
            "publishedAt": "2012-08-22T18:41:03.000Z",
            "cover": "https://i.ytimg.com/vi/0HxZn6CzOIo/hqdefault.jpg"
        }

        url = self.reverse('api:v1:providers:youtube:searchs')
        response = self.client.post(
            url, json.dumps(queries), content_type='application/json')

        self.assertEqual(
            expected,
            json.loads(response.content.decode('utf-8'))['1'][0])
