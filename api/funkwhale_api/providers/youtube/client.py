import threading

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

from dynamic_preferences.registries import global_preferences_registry as registry

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
VIDEO_BASE_URL = "https://www.youtube.com/watch?v={0}"


def _do_search(query):
    manager = registry.manager()
    youtube = build(
        YOUTUBE_API_SERVICE_NAME,
        YOUTUBE_API_VERSION,
        developerKey=manager["providers_youtube__api_key"],
    )

    return youtube.search().list(q=query, part="id,snippet", maxResults=25).execute()


class Client(object):
    def search(self, query):
        search_response = _do_search(query)
        videos = []
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                search_result["full_url"] = VIDEO_BASE_URL.format(
                    search_result["id"]["videoId"]
                )
                videos.append(search_result)
        return videos

    def search_multiple(self, queries):
        results = {}

        def search(key, query):
            results[key] = self.search(query)

        threads = [
            threading.Thread(target=search, args=(key, query))
            for key, query in queries.items()
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        return results

    def to_funkwhale(self, result):
        """
        We convert youtube results to something more generic.

        {
            "id": "video id",
            "type": "youtube#video",
            "url": "https://www.youtube.com/watch?v=id",
            "description": "description",
            "channelId": "Channel id",
            "title": "Title",
            "channelTitle": "channel Title",
            "publishedAt": "2012-08-22T18:41:03.000Z",
            "cover": "http://coverurl"
        }
        """
        return {
            "id": result["id"]["videoId"],
            "url": "https://www.youtube.com/watch?v={}".format(result["id"]["videoId"]),
            "type": result["id"]["kind"],
            "title": result["snippet"]["title"],
            "description": result["snippet"]["description"],
            "channelId": result["snippet"]["channelId"],
            "channelTitle": result["snippet"]["channelTitle"],
            "publishedAt": result["snippet"]["publishedAt"],
            "cover": result["snippet"]["thumbnails"]["high"]["url"],
        }


client = Client()
