from rest_framework import routers
from django.conf.urls import include, url
from funkwhale_api.music import views
from funkwhale_api.playlists import views as playlists_views
from rest_framework_jwt import views as jwt_views


router = routers.SimpleRouter()
router.register(r'tags', views.TagViewSet, 'tags')
router.register(r'tracks', views.TrackViewSet, 'tracks')
router.register(r'artists', views.ArtistViewSet, 'artists')
router.register(r'albums', views.AlbumViewSet, 'albums')
router.register(r'import-batches', views.ImportBatchViewSet, 'import-batches')
router.register(r'submit', views.SubmitViewSet, 'submit')
router.register(r'playlists', playlists_views.PlaylistViewSet, 'playlists')
router.register(r'playlist-tracks', playlists_views.PlaylistTrackViewSet, 'playlist-tracks')
urlpatterns = router.urls

urlpatterns += [
    url(r'^providers/', include('funkwhale_api.providers.urls', namespace='providers')),
    url(r'^favorites/', include('funkwhale_api.favorites.urls', namespace='favorites')),
    url(r'^search$', views.Search.as_view(), name='search'),
    url(r'^radios/', include('funkwhale_api.radios.urls', namespace='radios')),
    url(r'^history/', include('funkwhale_api.history.urls', namespace='history')),
    url(r'^users/', include('funkwhale_api.users.api_urls', namespace='users')),
    url(r'^token/', jwt_views.obtain_jwt_token),
    url(r'^token/refresh/', jwt_views.refresh_jwt_token),
]
