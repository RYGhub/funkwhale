from django.conf import settings

from rest_framework import serializers

from funkwhale_api.common import preferences
from funkwhale_api.common import middleware
from funkwhale_api.common import utils
from funkwhale_api.federation import utils as federation_utils

from . import models


def actor_detail_username(request, username, redirect_to_ap):
    validator = federation_utils.get_actor_data_from_username
    try:
        username_data = validator(username)
    except serializers.ValidationError:
        return []

    queryset = (
        models.Actor.objects.filter(
            preferred_username__iexact=username_data["username"]
        )
        .local()
        .select_related("attachment_icon")
    )
    try:
        obj = queryset.get()
    except models.Actor.DoesNotExist:
        return []

    if redirect_to_ap:
        raise middleware.ApiRedirect(obj.fid)
    obj_url = utils.join_url(
        settings.FUNKWHALE_URL,
        utils.spa_reverse("actor_detail", kwargs={"username": obj.preferred_username}),
    )
    metas = [
        {"tag": "meta", "property": "og:url", "content": obj_url},
        {"tag": "meta", "property": "og:title", "content": obj.display_name},
        {"tag": "meta", "property": "og:type", "content": "profile"},
    ]

    if obj.attachment_icon:
        metas.append(
            {
                "tag": "meta",
                "property": "og:image",
                "content": obj.attachment_icon.download_url_medium_square_crop,
            }
        )

    if preferences.get("federation__enabled"):
        metas.append(
            {
                "tag": "link",
                "rel": "alternate",
                "type": "application/activity+json",
                "href": obj.fid,
            }
        )

    return metas
