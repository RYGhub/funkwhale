from rest_framework import routers

from . import views

router = routers.SimpleRouter(trailing_slash=False)
router.register(
    r'federation/instance',
    views.InstanceViewSet,
    'instance')
router.register(
    r'.well-known',
    views.WellKnownViewSet,
    'well-known')

urlpatterns = router.urls
