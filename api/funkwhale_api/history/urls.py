from . import views

from rest_framework import routers

router = routers.SimpleRouter()
router.register(r"listenings", views.ListeningViewSet, "listenings")

urlpatterns = router.urls
