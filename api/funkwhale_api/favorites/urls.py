from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register(r"tracks", views.TrackFavoriteViewSet, "tracks")

urlpatterns = router.urls
