import urllib.parse

from django.conf import settings
from django.urls import reverse
from django.db.models import Q

from funkwhale_api.common import preferences
from funkwhale_api.common import middleware
from funkwhale_api.common import utils
from funkwhale_api.playlists import models as playlists_models

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


def library_track(request, pk, redirect_to_ap):
    queryset = models.Track.objects.filter(pk=pk).select_related("album", "artist")
    try:
        obj = queryset.get()
    except models.Track.DoesNotExist:
        return []

    playable_uploads = obj.uploads.playable_by(None).order_by("id")
    upload = playable_uploads.first()

    if redirect_to_ap:
        redirect_url = upload.fid if upload else obj.fid
        raise middleware.ApiRedirect(redirect_url)

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
    ]

    if obj.album:
        metas.append(
            {
                "tag": "meta",
                "property": "music:album",
                "content": utils.join_url(
                    settings.FUNKWHALE_URL,
                    utils.spa_reverse("library_album", kwargs={"pk": obj.album.pk}),
                ),
            },
        )

    if obj.attachment_cover:
        metas.append(
            {
                "tag": "meta",
                "property": "og:image",
                "content": obj.attachment_cover.download_url_medium_square_crop,
            }
        )
    elif obj.album and obj.album.attachment_cover:
        metas.append(
            {
                "tag": "meta",
                "property": "og:image",
                "content": obj.album.attachment_cover.download_url_medium_square_crop,
            }
        )
    if upload:
        metas.append(
            {
                "tag": "meta",
                "property": "og:audio",
                "content": utils.join_url(settings.FUNKWHALE_URL, obj.listen_url),
            }
        )
        if preferences.get("federation__enabled"):
            metas.append(
                {
                    "tag": "link",
                    "rel": "alternate",
                    "type": "application/activity+json",
                    "href": upload.fid,
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


def library_album(request, pk, redirect_to_ap):
    queryset = models.Album.objects.filter(pk=pk).select_related("artist")
    try:
        obj = queryset.get()
    except models.Album.DoesNotExist:
        return []

    if redirect_to_ap:
        raise middleware.ApiRedirect(obj.fid)

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

    if obj.attachment_cover:
        metas.append(
            {
                "tag": "meta",
                "property": "og:image",
                "content": obj.attachment_cover.download_url_medium_square_crop,
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


def library_artist(request, pk, redirect_to_ap):
    queryset = models.Artist.objects.filter(pk=pk)
    try:
        obj = queryset.get()
    except models.Artist.DoesNotExist:
        return []

    if redirect_to_ap:
        raise middleware.ApiRedirect(obj.fid)

    artist_url = utils.join_url(
        settings.FUNKWHALE_URL,
        utils.spa_reverse("library_artist", kwargs={"pk": obj.pk}),
    )
    # we use latest album's cover as artist image
    latest_album = (
        obj.albums.exclude(attachment_cover=None).order_by("release_date").last()
    )
    metas = [
        {"tag": "meta", "property": "og:url", "content": artist_url},
        {"tag": "meta", "property": "og:title", "content": obj.name},
        {"tag": "meta", "property": "og:type", "content": "profile"},
    ]

    if latest_album and latest_album.attachment_cover:
        metas.append(
            {
                "tag": "meta",
                "property": "og:image",
                "content": latest_album.attachment_cover.download_url_medium_square_crop,
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


def library_playlist(request, pk, redirect_to_ap):
    queryset = playlists_models.Playlist.objects.filter(pk=pk, privacy_level="everyone")
    try:
        obj = queryset.get()
    except playlists_models.Playlist.DoesNotExist:
        return []
    obj_url = utils.join_url(
        settings.FUNKWHALE_URL,
        utils.spa_reverse("library_playlist", kwargs={"pk": obj.pk}),
    )
    # we use the first playlist track's album's cover as image
    playlist_tracks = obj.playlist_tracks.exclude(track__album__attachment_cover=None)
    playlist_tracks = playlist_tracks.select_related("track__album").order_by("index")
    first_playlist_track = playlist_tracks.first()
    metas = [
        {"tag": "meta", "property": "og:url", "content": obj_url},
        {"tag": "meta", "property": "og:title", "content": obj.name},
        {"tag": "meta", "property": "og:type", "content": "music.playlist"},
    ]

    if first_playlist_track:
        metas.append(
            {
                "tag": "meta",
                "property": "og:image",
                "content": first_playlist_track.track.album.attachment_cover.download_url_medium_square_crop,
            }
        )

    if (
        models.Upload.objects.filter(
            track__pk__in=[obj.playlist_tracks.values("track")]
        )
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
                    + "?format=json&url={}".format(urllib.parse.quote_plus(obj_url))
                ),
            }
        )
        # twitter player is also supported in various software
        metas += get_twitter_card_metas(type="playlist", id=obj.pk)
    return metas


def library_library(request, uuid, redirect_to_ap):
    queryset = models.Library.objects.filter(uuid=uuid)
    try:
        obj = queryset.get()
    except models.Library.DoesNotExist:
        return []

    if redirect_to_ap:
        raise middleware.ApiRedirect(obj.fid)

    library_url = utils.join_url(
        settings.FUNKWHALE_URL,
        utils.spa_reverse("library_library", kwargs={"uuid": obj.uuid}),
    )
    metas = [
        {"tag": "meta", "property": "og:url", "content": library_url},
        {"tag": "meta", "property": "og:type", "content": "website"},
        {"tag": "meta", "property": "og:title", "content": obj.name},
        {"tag": "meta", "property": "og:description", "content": obj.description},
    ]

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
