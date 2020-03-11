from funkwhale_api.common import utils


def test_channel_detail(spa_html, no_api_auth, client, factories, settings):
    icon = factories["common.Attachment"]()
    actor = factories["federation.Actor"](local=True, attachment_icon=icon)
    url = "/@{}".format(actor.preferred_username)

    response = client.get(url)

    assert response.status_code == 200
    expected_metas = [
        {
            "tag": "meta",
            "property": "og:url",
            "content": utils.join_url(settings.FUNKWHALE_URL, url),
        },
        {"tag": "meta", "property": "og:title", "content": actor.display_name},
        {"tag": "meta", "property": "og:type", "content": "profile"},
        {
            "tag": "meta",
            "property": "og:image",
            "content": actor.attachment_icon.download_url_medium_square_crop,
        },
        {
            "tag": "link",
            "rel": "alternate",
            "type": "application/activity+json",
            "href": actor.fid,
        },
    ]

    metas = utils.parse_meta(response.content.decode())

    # we only test our custom metas, not the default ones
    assert metas[: len(expected_metas)] == expected_metas
