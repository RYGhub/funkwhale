import pytest

import urllib.parse

from django.urls import reverse

from funkwhale_api.common import utils
from funkwhale_api.federation import utils as federation_utils
from funkwhale_api.music import serializers


@pytest.mark.parametrize("attribute", ["uuid", "actor.full_username"])
def test_channel_detail(attribute, spa_html, no_api_auth, client, factories, settings):
    channel = factories["audio.Channel"](library__privacy_level="everyone")
    factories["music.Upload"](playable=True, library=channel.library)
    url = "/channels/{}".format(utils.recursive_getattr(channel, attribute))
    detail_url = "/channels/{}".format(channel.actor.full_username)

    response = client.get(url)

    assert response.status_code == 200
    expected_metas = [
        {
            "tag": "meta",
            "property": "og:url",
            "content": utils.join_url(settings.FUNKWHALE_URL, detail_url),
        },
        {"tag": "meta", "property": "og:title", "content": channel.artist.name},
        {"tag": "meta", "property": "og:type", "content": "profile"},
        {
            "tag": "meta",
            "property": "og:image",
            "content": channel.artist.attachment_cover.download_url_medium_square_crop,
        },
        {
            "tag": "link",
            "rel": "alternate",
            "type": "application/activity+json",
            "href": channel.actor.fid,
        },
        {
            "tag": "link",
            "rel": "alternate",
            "type": "application/rss+xml",
            "href": channel.get_rss_url(),
            "title": "{} - RSS Podcast Feed".format(channel.artist.name),
        },
        {
            "tag": "link",
            "rel": "alternate",
            "type": "application/json+oembed",
            "href": (
                utils.join_url(settings.FUNKWHALE_URL, reverse("api:v1:oembed"))
                + "?format=json&url={}".format(
                    urllib.parse.quote_plus(
                        utils.join_url(settings.FUNKWHALE_URL, detail_url)
                    )
                )
            ),
        },
        {"tag": "meta", "property": "twitter:card", "content": "player"},
        {
            "tag": "meta",
            "property": "twitter:player",
            "content": serializers.get_embed_url("channel", id=channel.uuid),
        },
        {"tag": "meta", "property": "twitter:player:width", "content": "600"},
        {"tag": "meta", "property": "twitter:player:height", "content": "400"},
    ]

    metas = utils.parse_meta(response.content.decode())

    # we only test our custom metas, not the default ones
    assert metas[: len(expected_metas)] == expected_metas


def test_oembed_channel(factories, no_api_auth, api_client, settings):
    settings.FUNKWHALE_URL = "http://test"
    settings.FUNKWHALE_EMBED_URL = "http://embed"
    channel = factories["audio.Channel"]()
    artist = channel.artist
    url = reverse("api:v1:oembed")
    obj_url = "https://test.com/channels/{}".format(channel.uuid)
    iframe_src = "http://embed?type=channel&id={}".format(channel.uuid)
    expected = {
        "version": "1.0",
        "type": "rich",
        "provider_name": settings.APP_NAME,
        "provider_url": settings.FUNKWHALE_URL,
        "height": 400,
        "width": 600,
        "title": artist.name,
        "description": artist.name,
        "thumbnail_url": federation_utils.full_url(
            artist.attachment_cover.file.crop["200x200"].url
        ),
        "thumbnail_height": 200,
        "thumbnail_width": 200,
        "html": '<iframe width="600" height="400" scrolling="no" frameborder="no" src="{}"></iframe>'.format(
            iframe_src
        ),
        "author_name": artist.name,
        "author_url": federation_utils.full_url(
            utils.spa_reverse("channel_detail", kwargs={"uuid": channel.uuid})
        ),
    }

    response = api_client.get(url, {"url": obj_url, "format": "json"})

    assert response.data == expected
