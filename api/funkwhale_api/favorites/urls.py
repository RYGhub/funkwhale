from funkwhale_api.common import routers

from . import views

router = routers.OptionalSlashRouter()
router.register(r"tracks", views.TrackFavoriteViewSet, "tracks")

urlpatterns = router.urls
