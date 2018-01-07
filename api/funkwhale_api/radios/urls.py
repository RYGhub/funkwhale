from django.conf.urls import include, url
from . import views

from rest_framework import routers
router = routers.SimpleRouter()
router.register(r'sessions', views.RadioSessionViewSet, 'sessions')
router.register(r'radios', views.RadioViewSet, 'radios')
router.register(r'tracks', views.RadioSessionTrackViewSet, 'tracks')


urlpatterns = router.urls
