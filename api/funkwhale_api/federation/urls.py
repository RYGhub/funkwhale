from rest_framework import routers

from . import views

router = routers.SimpleRouter(trailing_slash=False)
router.register(
    r'federation/instance/actors',
    views.InstanceActorViewSet,
    'instance-actors')
router.register(
    r'.well-known',
    views.WellKnownViewSet,
    'well-known')

urlpatterns = router.urls
