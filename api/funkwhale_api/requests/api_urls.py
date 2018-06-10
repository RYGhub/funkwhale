from . import views

from rest_framework import routers

router = routers.SimpleRouter()
router.register(r"import-requests", views.ImportRequestViewSet, "import-requests")

urlpatterns = router.urls
