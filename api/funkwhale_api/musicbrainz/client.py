import memoize.djangocache
import musicbrainzngs
from django.conf import settings

from funkwhale_api import __version__

_api = musicbrainzngs
_api.set_useragent("funkwhale", str(__version__), settings.FUNKWHALE_URL)
_api.set_hostname(settings.MUSICBRAINZ_HOSTNAME)


store = memoize.djangocache.Cache("default")
memo = memoize.Memoizer(store, namespace="memoize:musicbrainz")


def clean_artist_search(query, **kwargs):
    cleaned_kwargs = {}
    if kwargs.get("name"):
        cleaned_kwargs["artist"] = kwargs.get("name")
    return _api.search_artists(query, **cleaned_kwargs)


class API(object):
    _api = _api

    class artists(object):
        search = memo(clean_artist_search, max_age=settings.MUSICBRAINZ_CACHE_DURATION)
        get = memo(_api.get_artist_by_id, max_age=settings.MUSICBRAINZ_CACHE_DURATION)

    class images(object):
        get_front = memo(
            _api.get_image_front, max_age=settings.MUSICBRAINZ_CACHE_DURATION
        )

    class recordings(object):
        search = memo(
            _api.search_recordings, max_age=settings.MUSICBRAINZ_CACHE_DURATION
        )
        get = memo(
            _api.get_recording_by_id, max_age=settings.MUSICBRAINZ_CACHE_DURATION
        )

    class releases(object):
        search = memo(_api.search_releases, max_age=settings.MUSICBRAINZ_CACHE_DURATION)
        get = memo(_api.get_release_by_id, max_age=settings.MUSICBRAINZ_CACHE_DURATION)
        browse = memo(_api.browse_releases, max_age=settings.MUSICBRAINZ_CACHE_DURATION)
        # get_image_front = _api.get_image_front

    class release_groups(object):
        search = memo(
            _api.search_release_groups, max_age=settings.MUSICBRAINZ_CACHE_DURATION
        )
        get = memo(
            _api.get_release_group_by_id, max_age=settings.MUSICBRAINZ_CACHE_DURATION
        )
        browse = memo(
            _api.browse_release_groups, max_age=settings.MUSICBRAINZ_CACHE_DURATION
        )
        # get_image_front = _api.get_image_front


api = API()
