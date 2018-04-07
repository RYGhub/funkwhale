from django.conf.urls import include, url

from rest_framework import routers
from . import views

router = routers.SimpleRouter(trailing_slash=False)
music_router = routers.SimpleRouter(trailing_slash=False)
router.register(
    r'federation/instance/actors',
    views.InstanceActorViewSet,
    'instance-actors')
router.register(
    r'.well-known',
    views.WellKnownViewSet,
    'well-known')

music_router.register(
    r'files',
    views.MusicFilesViewSet,
    'files',
)
urlpatterns = router.urls + [
    url('federation/music/', include((music_router.urls, 'music'), namespace='music'))
]
