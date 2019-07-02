from funkwhale_api.common import routers

from . import views

router = routers.OptionalSlashRouter()
router.register(r"listenings", views.ListeningViewSet, "listenings")

urlpatterns = router.urls
