from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register(r"content-filters", views.UserFilterViewSet, "content-filters")

urlpatterns = router.urls
