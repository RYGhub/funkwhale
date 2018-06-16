from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register(r"listenings", views.ListeningViewSet, "listenings")

urlpatterns = router.urls
