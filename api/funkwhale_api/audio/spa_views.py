import urllib.parse

from django.conf import settings
from django.urls import reverse

from funkwhale_api.common import preferences
from funkwhale_api.common import utils
from funkwhale_api.music import spa_views

from . import models


def channel_detail(request, uuid):
    queryset = models.Channel.objects.filter(uuid=uuid).select_related(
        "artist__attachment_cover", "actor", "library"
    )
    try:
        obj = queryset.get()
    except models.Channel.DoesNotExist:
        return []
    obj_url = utils.join_url(
        settings.FUNKWHALE_URL,
        utils.spa_reverse("channel_detail", kwargs={"uuid": obj.uuid}),
    )
    metas = [
        {"tag": "meta", "property": "og:url", "content": obj_url},
        {"tag": "meta", "property": "og:title", "content": obj.artist.name},
        {"tag": "meta", "property": "og:type", "content": "profile"},
    ]

    if obj.artist.attachment_cover:
        metas.append(
            {
                "tag": "meta",
                "property": "og:image",
                "content": obj.artist.attachment_cover.download_url_medium_square_crop,
            }
        )

    if preferences.get("federation__enabled"):
        metas.append(
            {
                "tag": "link",
                "rel": "alternate",
                "type": "application/activity+json",
                "href": obj.actor.fid,
            }
        )

    metas.append(
        {
            "tag": "link",
            "rel": "alternate",
            "type": "application/rss+xml",
            "href": obj.get_rss_url(),
            "title": "{} - RSS Podcast Feed".format(obj.artist.name),
        },
    )

    if obj.library.uploads.all().playable_by(None).exists():
        metas.append(
            {
                "tag": "link",
                "rel": "alternate",
                "type": "application/json+oembed",
                "href": (
                    utils.join_url(settings.FUNKWHALE_URL, reverse("api:v1:oembed"))
                    + "?format=json&url={}".format(urllib.parse.quote_plus(obj_url))
                ),
            }
        )
        # twitter player is also supported in various software
        metas += spa_views.get_twitter_card_metas(type="channel", id=obj.uuid)
    return metas
