import threading

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

from django.conf import settings

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = settings.FUNKWHALE_PROVIDERS['youtube']['api_key']
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
VIDEO_BASE_URL = 'https://www.youtube.com/watch?v={0}'


def _do_search(query):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

    return youtube.search().list(
        q=query,
        part="id,snippet",
        maxResults=25
    ).execute()


class Client(object):

    def search(self, query):
        search_response = _do_search(query)
        videos = []
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                search_result['full_url'] = VIDEO_BASE_URL.format(search_result["id"]['videoId'])
                videos.append(search_result)
        return videos

    def search_multiple(self, queries):
        results = {}

        def search(key, query):
            results[key] = self.search(query)

        threads = [
            threading.Thread(target=search, args=(key, query,))
            for key, query in queries.items()
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        return results

client = Client()
