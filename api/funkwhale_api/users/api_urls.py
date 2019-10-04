from funkwhale_api.common import routers

from . import views

router = routers.OptionalSlashRouter()
router.register(r"users", views.UserViewSet, "users")

urlpatterns = router.urls
