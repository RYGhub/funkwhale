from django import urls

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
]
