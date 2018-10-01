from django.conf.urls import include, url
from dynamic_preferences.api.viewsets import GlobalPreferencesViewSet
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_jwt import views as jwt_views

from funkwhale_api.activity import views as activity_views
from funkwhale_api.music import views
from funkwhale_api.playlists import views as playlists_views
from funkwhale_api.subsonic.views import SubsonicViewSet

router = routers.SimpleRouter()
router.register(r"settings", GlobalPreferencesViewSet, base_name="settings")
router.register(r"activity", activity_views.ActivityViewSet, "activity")
router.register(r"tags", views.TagViewSet, "tags")
router.register(r"tracks", views.TrackViewSet, "tracks")
router.register(r"uploads", views.UploadViewSet, "uploads")
router.register(r"libraries", views.LibraryViewSet, "libraries")
router.register(r"listen", views.ListenViewSet, "listen")
router.register(r"artists", views.ArtistViewSet, "artists")
router.register(r"albums", views.AlbumViewSet, "albums")
router.register(r"playlists", playlists_views.PlaylistViewSet, "playlists")
router.register(
    r"playlist-tracks", playlists_views.PlaylistTrackViewSet, "playlist-tracks"
)
v1_patterns = router.urls

subsonic_router = routers.SimpleRouter(trailing_slash=False)
subsonic_router.register(r"subsonic/rest", SubsonicViewSet, base_name="subsonic")


v1_patterns += [
    url(
        r"^instance/",
        include(("funkwhale_api.instance.urls", "instance"), namespace="instance"),
    ),
    url(
        r"^manage/",
        include(("funkwhale_api.manage.urls", "manage"), namespace="manage"),
    ),
    url(
        r"^federation/",
        include(
            ("funkwhale_api.federation.api_urls", "federation"), namespace="federation"
        ),
    ),
    url(
        r"^providers/",
        include(("funkwhale_api.providers.urls", "providers"), namespace="providers"),
    ),
    url(
        r"^favorites/",
        include(("funkwhale_api.favorites.urls", "favorites"), namespace="favorites"),
    ),
    url(r"^search$", views.Search.as_view(), name="search"),
    url(
        r"^radios/",
        include(("funkwhale_api.radios.urls", "radios"), namespace="radios"),
    ),
    url(
        r"^history/",
        include(("funkwhale_api.history.urls", "history"), namespace="history"),
    ),
    url(
        r"^users/",
        include(("funkwhale_api.users.api_urls", "users"), namespace="users"),
    ),
    url(r"^token/$", jwt_views.obtain_jwt_token, name="token"),
    url(r"^token/refresh/$", jwt_views.refresh_jwt_token, name="token_refresh"),
]

urlpatterns = [
    url(r"^v1/", include((v1_patterns, "v1"), namespace="v1"))
] + format_suffix_patterns(subsonic_router.urls, allowed=["view"])
