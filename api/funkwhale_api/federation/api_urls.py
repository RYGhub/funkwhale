from funkwhale_api.common import routers

from . import api_views

router = routers.OptionalSlashRouter()
router.register(r"fetches", api_views.FetchViewSet, "fetches")
router.register(r"follows/library", api_views.LibraryFollowViewSet, "library-follows")
router.register(r"inbox", api_views.InboxItemViewSet, "inbox")
router.register(r"libraries", api_views.LibraryViewSet, "libraries")
router.register(r"domains", api_views.DomainViewSet, "domains")
router.register(r"actors", api_views.ActorViewSet, "actors")

urlpatterns = router.urls
