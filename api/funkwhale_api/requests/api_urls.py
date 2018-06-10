from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register(r"import-requests", views.ImportRequestViewSet, "import-requests")

urlpatterns = router.urls
