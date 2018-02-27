from django.conf.urls import url
from django.views.decorators.cache import cache_page

from . import views


urlpatterns = [
    url(r'^settings/$', views.InstanceSettings.as_view(), name='settings'),
    url(r'^stats/$',
        cache_page(60 * 5)(views.InstanceStats.as_view()), name='stats'),
]
