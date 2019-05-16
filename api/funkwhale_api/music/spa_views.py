import urllib.parse

from django.conf import settings
from django.urls import reverse
from django.db.models import Q

from funkwhale_api.common import utils

from . import models
from . import serializers


def get_twitter_card_metas(type, id):
    return [
        {"tag": "meta", "property": "twitter:card", "content": "player"},
        {
            "tag": "meta",
            "property": "twitter:player",
            "content": serializers.get_embed_url(type, id),
        },
        {"tag": "meta", "property": "twitter:player:width", "content": "600"},
        {"tag": "meta", "property": "twitter:player:height", "content": "400"},
    ]


def library_track(request, pk):
    queryset = models.Track.objects.filter(pk=pk).select_related("album", "artist")
    try:
        obj = queryset.get()
    except models.Track.DoesNotExist:
        return []
    track_url = utils.join_url(
        settings.FUNKWHALE_URL,
        utils.spa_reverse("library_track", kwargs={"pk": obj.pk}),
    )
    metas = [
        {"tag": "meta", "property": "og:url", "content": track_url},
        {"tag": "meta", "property": "og:title", "content": obj.title},
        {"tag": "meta", "property": "og:type", "content": "music.song"},
        {"tag": "meta", "property": "music:album:disc", "content": obj.disc_number},
        {"tag": "meta", "property": "music:album:track", "content": obj.position},
        {
            "tag": "meta",
            "property": "music:musician",
            "content": utils.join_url(
                settings.FUNKWHALE_URL,
                utils.spa_reverse("library_artist", kwargs={"pk": obj.artist.pk}),
            ),
        },
        {
            "tag": "meta",
            "property": "music:album",
            "content": utils.join_url(
                settings.FUNKWHALE_URL,
                utils.spa_reverse("library_album", kwargs={"pk": obj.album.pk}),
            ),
        },
    ]
    if obj.album.cover:
        metas.append(
            {
                "tag": "meta",
                "property": "og:image",
                "content": utils.join_url(
                    settings.FUNKWHALE_URL, obj.album.cover.crop["400x400"].url
                ),
            }
        )

    if obj.uploads.playable_by(None).exists():
        metas.append(
            {
                "tag": "meta",
                "property": "og:audio",
                "content": utils.join_url(settings.FUNKWHALE_URL, obj.listen_url),
            }
        )

        metas.append(
            {
                "tag": "link",
                "rel": "alternate",
                "type": "application/json+oembed",
                "href": (
                    utils.join_url(settings.FUNKWHALE_URL, reverse("api:v1:oembed"))
                    + "?format=json&url={}".format(urllib.parse.quote_plus(track_url))
                ),
            }
        )
        # twitter player is also supported in various software
        metas += get_twitter_card_metas(type="track", id=obj.pk)
    return metas


def library_album(request, pk):
    queryset = models.Album.objects.filter(pk=pk).select_related("artist")
    try:
        obj = queryset.get()
    except models.Album.DoesNotExist:
        return []
    album_url = utils.join_url(
        settings.FUNKWHALE_URL,
        utils.spa_reverse("library_album", kwargs={"pk": obj.pk}),
    )
    metas = [
        {"tag": "meta", "property": "og:url", "content": album_url},
        {"tag": "meta", "property": "og:title", "content": obj.title},
        {"tag": "meta", "property": "og:type", "content": "music.album"},
        {
            "tag": "meta",
            "property": "music:musician",
            "content": utils.join_url(
                settings.FUNKWHALE_URL,
                utils.spa_reverse("library_artist", kwargs={"pk": obj.artist.pk}),
            ),
        },
    ]

    if obj.release_date:
        metas.append(
            {
                "tag": "meta",
                "property": "music:release_date",
                "content": str(obj.release_date),
            }
        )

    if obj.cover:
        metas.append(
            {
                "tag": "meta",
                "property": "og:image",
                "content": utils.join_url(
                    settings.FUNKWHALE_URL, obj.cover.crop["400x400"].url
                ),
            }
        )

    if models.Upload.objects.filter(track__album=obj).playable_by(None).exists():
        metas.append(
            {
                "tag": "link",
                "rel": "alternate",
                "type": "application/json+oembed",
                "href": (
                    utils.join_url(settings.FUNKWHALE_URL, reverse("api:v1:oembed"))
                    + "?format=json&url={}".format(urllib.parse.quote_plus(album_url))
                ),
            }
        )
        # twitter player is also supported in various software
        metas += get_twitter_card_metas(type="album", id=obj.pk)
    return metas


def library_artist(request, pk):
    queryset = models.Artist.objects.filter(pk=pk)
    try:
        obj = queryset.get()
    except models.Artist.DoesNotExist:
        return []
    artist_url = utils.join_url(
        settings.FUNKWHALE_URL,
        utils.spa_reverse("library_artist", kwargs={"pk": obj.pk}),
    )
    # we use latest album's cover as artist image
    latest_album = (
        obj.albums.exclude(cover="").exclude(cover=None).order_by("release_date").last()
    )
    metas = [
        {"tag": "meta", "property": "og:url", "content": artist_url},
        {"tag": "meta", "property": "og:title", "content": obj.name},
        {"tag": "meta", "property": "og:type", "content": "profile"},
    ]

    if latest_album and latest_album.cover:
        metas.append(
            {
                "tag": "meta",
                "property": "og:image",
                "content": utils.join_url(
                    settings.FUNKWHALE_URL, latest_album.cover.crop["400x400"].url
                ),
            }
        )

    if (
        models.Upload.objects.filter(Q(track__artist=obj) | Q(track__album__artist=obj))
        .playable_by(None)
        .exists()
    ):
        metas.append(
            {
                "tag": "link",
                "rel": "alternate",
                "type": "application/json+oembed",
                "href": (
                    utils.join_url(settings.FUNKWHALE_URL, reverse("api:v1:oembed"))
                    + "?format=json&url={}".format(urllib.parse.quote_plus(artist_url))
                ),
            }
        )
        # twitter player is also supported in various software
        metas += get_twitter_card_metas(type="artist", id=obj.pk)
    return metas
