from funkwhale_api.common import routers

from . import views

router = routers.OptionalSlashRouter()
router.register(r"sessions", views.RadioSessionViewSet, "sessions")
router.register(r"radios", views.RadioViewSet, "radios")
router.register(r"tracks", views.RadioSessionTrackViewSet, "tracks")


urlpatterns = router.urls
