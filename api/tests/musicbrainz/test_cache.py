from funkwhale_api.musicbrainz import client


def test_can_search_recording_in_musicbrainz_api(mocker):
    r = {"hello": "world"}
    m = mocker.patch(
        "funkwhale_api.musicbrainz.client._api.search_artists", return_value=r
    )
    assert client.api.artists.search("test") == r
    # now call from cache
    assert client.api.artists.search("test") == r
    assert client.api.artists.search("test") == r
    assert m.call_count == 1
