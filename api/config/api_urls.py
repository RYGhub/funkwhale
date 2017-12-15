from rest_framework import routers
from django.conf.urls import include, url
from funkwhale_api.music import views
from funkwhale_api.playlists import views as playlists_views
from rest_framework_jwt import views as jwt_views

from dynamic_preferences.api.viewsets import GlobalPreferencesViewSet
from dynamic_preferences.users.viewsets import UserPreferencesViewSet

router = routers.SimpleRouter()
router.register(r'settings', GlobalPreferencesViewSet, base_name='settings')
router.register(r'tags', views.TagViewSet, 'tags')
router.register(r'tracks', views.TrackViewSet, 'tracks')
router.register(r'trackfiles', views.TrackFileViewSet, 'trackfiles')
router.register(r'artists', views.ArtistViewSet, 'artists')
router.register(r'albums', views.AlbumViewSet, 'albums')
router.register(r'import-batches', views.ImportBatchViewSet, 'import-batches')
router.register(r'submit', views.SubmitViewSet, 'submit')
router.register(r'playlists', playlists_views.PlaylistViewSet, 'playlists')
router.register(
    r'playlist-tracks',
    playlists_views.PlaylistTrackViewSet,
    'playlist-tracks')
v1_patterns = router.urls

v1_patterns += [
    url(r'^providers/',
        include(
            ('funkwhale_api.providers.urls', 'providers'),
            namespace='providers')),
    url(r'^favorites/',
        include(
            ('funkwhale_api.favorites.urls', 'favorites'),
            namespace='favorites')),
    url(r'^search$',
        views.Search.as_view(), name='search'),
    url(r'^radios/',
        include(
            ('funkwhale_api.radios.urls', 'radios'),
            namespace='radios')),
    url(r'^history/',
        include(
            ('funkwhale_api.history.urls', 'history'),
            namespace='history')),
    url(r'^users/',
        include(
            ('funkwhale_api.users.api_urls', 'users'),
            namespace='users')),
    url(r'^token/',
        jwt_views.obtain_jwt_token),
    url(r'^token/refresh/', jwt_views.refresh_jwt_token),
]

urlpatterns = [
    url(r'^v1/', include((v1_patterns, 'v1'), namespace='v1'))
]
