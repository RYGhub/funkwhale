import memoize.djangocache

import funkwhale_api
from funkwhale_api.common import preferences
from funkwhale_api.federation import actors
from funkwhale_api.music import utils as music_utils

from . import stats

store = memoize.djangocache.Cache("default")
memo = memoize.Memoizer(store, namespace="instance:stats")


def get():
    share_stats = preferences.get("instance__nodeinfo_stats_enabled")
    data = {
        "version": "2.0",
        "software": {"name": "funkwhale", "version": funkwhale_api.__version__},
        "protocols": ["activitypub"],
        "services": {"inbound": [], "outbound": []},
        "openRegistrations": preferences.get("users__registration_enabled"),
        "usage": {"users": {"total": 0, "activeHalfyear": 0, "activeMonth": 0}},
        "metadata": {
            "actorId": actors.get_service_actor().fid,
            "private": preferences.get("instance__nodeinfo_private"),
            "shortDescription": preferences.get("instance__short_description"),
            "longDescription": preferences.get("instance__long_description"),
            "nodeName": preferences.get("instance__name"),
            "library": {
                "federationEnabled": preferences.get("federation__enabled"),
                "federationNeedsApproval": preferences.get(
                    "federation__music_needs_approval"
                ),
                "anonymousCanListen": not preferences.get(
                    "common__api_authentication_required"
                ),
            },
            "supportedUploadExtensions": music_utils.SUPPORTED_EXTENSIONS,
        },
    }
    if share_stats:
        getter = memo(lambda: stats.get(), max_age=600)
        statistics = getter()
        data["usage"]["users"]["total"] = statistics["users"]["total"]
        data["usage"]["users"]["activeHalfyear"] = statistics["users"][
            "active_halfyear"
        ]
        data["usage"]["users"]["activeMonth"] = statistics["users"]["active_month"]
        data["metadata"]["library"]["tracks"] = {"total": statistics["tracks"]}
        data["metadata"]["library"]["artists"] = {"total": statistics["artists"]}
        data["metadata"]["library"]["albums"] = {"total": statistics["albums"]}
        data["metadata"]["library"]["music"] = {"hours": statistics["music_duration"]}

        data["metadata"]["usage"] = {
            "favorites": {"tracks": {"total": statistics["track_favorites"]}},
            "listenings": {"total": statistics["listenings"]},
        }
    return data
