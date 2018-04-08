from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register(
    r'libraries',
    views.LibraryViewSet,
    'libraries')

urlpatterns = router.urls
