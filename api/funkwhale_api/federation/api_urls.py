from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register(
    r'libraries',
    views.LibraryViewSet,
    'libraries')
router.register(
    r'library-tracks',
    views.LibraryTrackViewSet,
    'library-tracks')

urlpatterns = router.urls
