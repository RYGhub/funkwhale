import urllib.parse

from django.urls import reverse

from funkwhale_api.common import utils
from funkwhale_api.music import serializers


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
            "content": utils.join_url(
                settings.FUNKWHALE_URL, track.album.cover.crop["400x400"].url
            ),
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
                + "?format=json&url={}".format(
                    urllib.parse.quote_plus(utils.join_url(settings.FUNKWHALE_URL, url))
                )
            ),
        },
        {"tag": "meta", "property": "twitter:card", "content": "player"},
        {
            "tag": "meta",
            "property": "twitter:player",
            "content": serializers.get_embed_url("track", id=track.id),
        },
        {"tag": "meta", "property": "twitter:player:width", "content": "600"},
        {"tag": "meta", "property": "twitter:player:height", "content": "400"},
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
            "content": utils.join_url(
                settings.FUNKWHALE_URL, album.cover.crop["400x400"].url
            ),
        },
        {
            "tag": "link",
            "rel": "alternate",
            "type": "application/json+oembed",
            "href": (
                utils.join_url(settings.FUNKWHALE_URL, reverse("api:v1:oembed"))
                + "?format=json&url={}".format(
                    urllib.parse.quote_plus(utils.join_url(settings.FUNKWHALE_URL, url))
                )
            ),
        },
        {"tag": "meta", "property": "twitter:card", "content": "player"},
        {
            "tag": "meta",
            "property": "twitter:player",
            "content": serializers.get_embed_url("album", id=album.id),
        },
        {"tag": "meta", "property": "twitter:player:width", "content": "600"},
        {"tag": "meta", "property": "twitter:player:height", "content": "400"},
    ]

    metas = utils.parse_meta(response.content.decode())

    # we only test our custom metas, not the default ones
    assert metas[: len(expected_metas)] == expected_metas


def test_library_artist(spa_html, no_api_auth, client, factories, settings):
    album = factories["music.Album"]()
    factories["music.Upload"](playable=True, track__album=album)
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
            "content": utils.join_url(
                settings.FUNKWHALE_URL, album.cover.crop["400x400"].url
            ),
        },
        {
            "tag": "link",
            "rel": "alternate",
            "type": "application/json+oembed",
            "href": (
                utils.join_url(settings.FUNKWHALE_URL, reverse("api:v1:oembed"))
                + "?format=json&url={}".format(
                    urllib.parse.quote_plus(utils.join_url(settings.FUNKWHALE_URL, url))
                )
            ),
        },
        {"tag": "meta", "property": "twitter:card", "content": "player"},
        {
            "tag": "meta",
            "property": "twitter:player",
            "content": serializers.get_embed_url("artist", id=artist.id),
        },
        {"tag": "meta", "property": "twitter:player:width", "content": "600"},
        {"tag": "meta", "property": "twitter:player:height", "content": "400"},
    ]

    metas = utils.parse_meta(response.content.decode())

    # we only test our custom metas, not the default ones
    assert metas[: len(expected_metas)] == expected_metas
