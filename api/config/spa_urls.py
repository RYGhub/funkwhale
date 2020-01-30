from django import urls

from funkwhale_api.audio import spa_views as audio_spa_views
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
        r"^channels/(?P<uuid>[0-9a-f-]+)/?$",
        audio_spa_views.channel_detail,
        name="channel_detail",
    ),
]
