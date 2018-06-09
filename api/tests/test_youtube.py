from collections import OrderedDict
from django.urls import reverse
from funkwhale_api.providers.youtube.client import client

from .data import youtube as api_data


def test_can_get_search_results_from_youtube(mocker):
    mocker.patch(
        "funkwhale_api.providers.youtube.client._do_search",
        return_value=api_data.search["8 bit adventure"],
    )
    query = "8 bit adventure"
    results = client.search(query)
    assert results[0]["id"]["videoId"] == "0HxZn6CzOIo"
    assert results[0]["snippet"]["title"] == "AdhesiveWombat - 8 Bit Adventure"
    assert results[0]["full_url"] == "https://www.youtube.com/watch?v=0HxZn6CzOIo"


def test_can_get_search_results_from_funkwhale(preferences, mocker, api_client, db):
    preferences["common__api_authentication_required"] = False
    mocker.patch(
        "funkwhale_api.providers.youtube.client._do_search",
        return_value=api_data.search["8 bit adventure"],
    )
    query = "8 bit adventure"
    url = reverse("api:v1:providers:youtube:search")
    response = api_client.get(url, {"query": query})
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
        "cover": "https://i.ytimg.com/vi/0HxZn6CzOIo/hqdefault.jpg",
    }

    assert response.data[0] == expected


def test_can_send_multiple_queries_at_once(mocker):
    mocker.patch(
        "funkwhale_api.providers.youtube.client._do_search",
        side_effect=[
            api_data.search["8 bit adventure"],
            api_data.search["system of a down toxicity"],
        ],
    )

    queries = OrderedDict()
    queries["1"] = {"q": "8 bit adventure"}
    queries["2"] = {"q": "system of a down toxicity"}

    results = client.search_multiple(queries)

    assert results["1"][0]["id"]["videoId"] == "0HxZn6CzOIo"
    assert results["1"][0]["snippet"]["title"] == "AdhesiveWombat - 8 Bit Adventure"
    assert results["1"][0]["full_url"] == "https://www.youtube.com/watch?v=0HxZn6CzOIo"
    assert results["2"][0]["id"]["videoId"] == "BorYwGi2SJc"
    assert results["2"][0]["snippet"]["title"] == "System of a Down: Toxicity"
    assert results["2"][0]["full_url"] == "https://www.youtube.com/watch?v=BorYwGi2SJc"


def test_can_send_multiple_queries_at_once_from_funwkhale(
    preferences, mocker, db, api_client
):
    preferences["common__api_authentication_required"] = False
    mocker.patch(
        "funkwhale_api.providers.youtube.client._do_search",
        return_value=api_data.search["8 bit adventure"],
    )
    queries = OrderedDict()
    queries["1"] = {"q": "8 bit adventure"}

    expected = {
        "id": "0HxZn6CzOIo",
        "url": "https://www.youtube.com/watch?v=0HxZn6CzOIo",
        "type": "youtube#video",
        "description": "Make sure to apply adhesive evenly before use. GET IT HERE: http://adhesivewombat.bandcamp.com/album/marsupial-madness Facebook: ...",
        "channelId": "UCps63j3krzAG4OyXeEyuhFw",
        "title": "AdhesiveWombat - 8 Bit Adventure",
        "channelTitle": "AdhesiveWombat",
        "publishedAt": "2012-08-22T18:41:03.000Z",
        "cover": "https://i.ytimg.com/vi/0HxZn6CzOIo/hqdefault.jpg",
    }

    url = reverse("api:v1:providers:youtube:searchs")
    response = api_client.post(url, queries, format="json")

    assert expected == response.data["1"][0]
