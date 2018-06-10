from . import views

from rest_framework import routers

router = routers.SimpleRouter()
router.register(r"tracks", views.TrackFavoriteViewSet, "tracks")

urlpatterns = router.urls
