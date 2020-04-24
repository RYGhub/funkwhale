import urllib.parse

from django.conf import settings
from django.db.models import Q
from django.urls import reverse

from rest_framework import serializers

from funkwhale_api.common import preferences
from funkwhale_api.common import middleware
from funkwhale_api.common import utils
from funkwhale_api.federation import utils as federation_utils
from funkwhale_api.music import spa_views

from . import models


def channel_detail(query, redirect_to_ap):
    queryset = models.Channel.objects.filter(query).select_related(
        "artist__attachment_cover", "actor", "library"
    )
    try:
        obj = queryset.get()
    except models.Channel.DoesNotExist:
        return []

    if redirect_to_ap:
        raise middleware.ApiRedirect(obj.actor.fid)

    obj_url = utils.join_url(
        settings.FUNKWHALE_URL,
        utils.spa_reverse(
            "channel_detail", kwargs={"username": obj.actor.full_username}
        ),
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


def channel_detail_uuid(request, uuid, redirect_to_ap):
    validator = serializers.UUIDField().to_internal_value
    try:
        uuid = validator(uuid)
    except serializers.ValidationError:
        return []
    return channel_detail(Q(uuid=uuid), redirect_to_ap)


def channel_detail_username(request, username, redirect_to_ap):
    validator = federation_utils.get_actor_data_from_username
    try:
        username_data = validator(username)
    except serializers.ValidationError:
        return []
    query = Q(
        actor__domain=username_data["domain"],
        actor__preferred_username__iexact=username_data["username"],
    )
    return channel_detail(query, redirect_to_ap)
