import musicbrainzngs

from django.conf import settings
from funkwhale_api import __version__
_api = musicbrainzngs
_api.set_useragent('funkwhale', str(__version__), 'contact@eliotberriot.com')


def clean_artist_search(query, **kwargs):
    cleaned_kwargs = {}
    if kwargs.get('name'):
        cleaned_kwargs['artist'] = kwargs.get('name')
    return _api.search_artists(query, **cleaned_kwargs)


class API(object):
    _api = _api

    class artists(object):
        search = clean_artist_search
        get = _api.get_artist_by_id

    class images(object):
        get_front = _api.get_image_front

    class recordings(object):
        search = _api.search_recordings
        get = _api.get_recording_by_id

    class works(object):
        search = _api.search_works
        get = _api.get_work_by_id

    class releases(object):
        search = _api.search_releases
        get = _api.get_release_by_id
        browse = _api.browse_releases
        # get_image_front = _api.get_image_front

    class release_groups(object):
        search = _api.search_release_groups
        get = _api.get_release_group_by_id
        browse = _api.browse_release_groups
        # get_image_front = _api.get_image_front

api = API()
