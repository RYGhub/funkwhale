from rest_framework import routers

from . import api_views

router = routers.SimpleRouter()
router.register(r"fetches", api_views.FetchViewSet, "fetches")
router.register(r"follows/library", api_views.LibraryFollowViewSet, "library-follows")
router.register(r"inbox", api_views.InboxItemViewSet, "inbox")
router.register(r"libraries", api_views.LibraryViewSet, "libraries")

urlpatterns = router.urls
