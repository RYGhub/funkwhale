from django import urls

from funkwhale_api.audio import spa_views as audio_spa_views
from funkwhale_api.federation import spa_views as federation_spa_views
from funkwhale_api.music import spa_views


urlpatterns = [
    urls.re_path(
        r"^library/tracks/(?P<pk>\d+)/?$", spa_views.library_track, name="library_track"
    ),
    urls.re_path(
        r"^library/albums/(?P<pk>\d+)/?$", spa_views.library_album, name="library_album"
    ),
    urls.re_path(
        r"^library/artists/(?P<pk>\d+)/?$",
        spa_views.library_artist,
        name="library_artist",
    ),
    urls.re_path(
        r"^library/playlists/(?P<pk>\d+)/?$",
        spa_views.library_playlist,
        name="library_playlist",
    ),
    urls.re_path(
        r"^library/(?P<uuid>[0-9a-f-]+)/?$",
        spa_views.library_library,
        name="library_library",
    ),
    urls.re_path(
        r"^channels/(?P<uuid>[0-9a-f-]+)/?$",
        audio_spa_views.channel_detail_uuid,
        name="channel_detail",
    ),
    urls.re_path(
        r"^channels/(?P<username>[^/]+)/?$",
        audio_spa_views.channel_detail_username,
        name="channel_detail",
    ),
    urls.re_path(
        r"^@(?P<username>[^/]+)/?$",
        federation_spa_views.actor_detail_username,
        name="actor_detail",
    ),
]
