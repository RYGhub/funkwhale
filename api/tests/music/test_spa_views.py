from django.urls import reverse

from funkwhale_api.common import utils


def test_library_track(spa_html, no_api_auth, client, factories, settings):
    track = factories["music.Upload"](playable=True, track__disc_number=1).track
    url = "/library/tracks/{}".format(track.pk)

    response = client.get(url)

    expected_metas = [
        {
            "tag": "meta",
            "property": "og:url",
            "content": utils.join_url(settings.FUNKWHALE_URL, url),
        },
        {"tag": "meta", "property": "og:title", "content": track.title},
        {"tag": "meta", "property": "og:type", "content": "music.song"},
        {
            "tag": "meta",
            "property": "music:album:disc",
            "content": str(track.disc_number),
        },
        {
            "tag": "meta",
            "property": "music:album:track",
            "content": str(track.position),
        },
        {
            "tag": "meta",
            "property": "music:musician",
            "content": utils.join_url(
                settings.FUNKWHALE_URL,
                utils.spa_reverse("library_artist", kwargs={"pk": track.artist.pk}),
            ),
        },
        {
            "tag": "meta",
            "property": "music:album",
            "content": utils.join_url(
                settings.FUNKWHALE_URL,
                utils.spa_reverse("library_album", kwargs={"pk": track.album.pk}),
            ),
        },
        {
            "tag": "meta",
            "property": "og:image",
            "content": utils.join_url(settings.FUNKWHALE_URL, track.album.cover.url),
        },
        {
            "tag": "meta",
            "property": "og:audio",
            "content": utils.join_url(settings.FUNKWHALE_URL, track.listen_url),
        },
        {
            "tag": "link",
            "rel": "alternate",
            "type": "application/json+oembed",
            "href": (
                utils.join_url(settings.FUNKWHALE_URL, reverse("api:v1:oembed"))
                + "?url={}".format(utils.join_url(settings.FUNKWHALE_URL, url))
            ),
        },
    ]

    metas = utils.parse_meta(response.content.decode())

    # we only test our custom metas, not the default ones
    assert metas[: len(expected_metas)] == expected_metas


def test_library_album(spa_html, no_api_auth, client, factories, settings):
    track = factories["music.Upload"](playable=True, track__disc_number=1).track
    album = track.album
    url = "/library/albums/{}".format(album.pk)

    response = client.get(url)

    expected_metas = [
        {
            "tag": "meta",
            "property": "og:url",
            "content": utils.join_url(settings.FUNKWHALE_URL, url),
        },
        {"tag": "meta", "property": "og:title", "content": album.title},
        {"tag": "meta", "property": "og:type", "content": "music.album"},
        {
            "tag": "meta",
            "property": "music:musician",
            "content": utils.join_url(
                settings.FUNKWHALE_URL,
                utils.spa_reverse("library_artist", kwargs={"pk": album.artist.pk}),
            ),
        },
        {
            "tag": "meta",
            "property": "music:release_date",
            "content": str(album.release_date),
        },
        {
            "tag": "meta",
            "property": "og:image",
            "content": utils.join_url(settings.FUNKWHALE_URL, album.cover.url),
        },
        {
            "tag": "link",
            "rel": "alternate",
            "type": "application/json+oembed",
            "href": (
                utils.join_url(settings.FUNKWHALE_URL, reverse("api:v1:oembed"))
                + "?url={}".format(utils.join_url(settings.FUNKWHALE_URL, url))
            ),
        },
    ]

    metas = utils.parse_meta(response.content.decode())

    # we only test our custom metas, not the default ones
    assert metas[: len(expected_metas)] == expected_metas


def test_library_artist(spa_html, no_api_auth, client, factories, settings):
    album = factories["music.Album"]()
    artist = album.artist
    url = "/library/artists/{}".format(artist.pk)

    response = client.get(url)

    expected_metas = [
        {
            "tag": "meta",
            "property": "og:url",
            "content": utils.join_url(settings.FUNKWHALE_URL, url),
        },
        {"tag": "meta", "property": "og:title", "content": artist.name},
        {"tag": "meta", "property": "og:type", "content": "profile"},
        {
            "tag": "meta",
            "property": "og:image",
            "content": utils.join_url(settings.FUNKWHALE_URL, album.cover.url),
        },
    ]

    metas = utils.parse_meta(response.content.decode())

    # we only test our custom metas, not the default ones
    assert metas[: len(expected_metas)] == expected_metas
