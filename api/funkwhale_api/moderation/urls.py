from funkwhale_api.common import routers

from . import views

router = routers.OptionalSlashRouter()
router.register(r"content-filters", views.UserFilterViewSet, "content-filters")

urlpatterns = router.urls
