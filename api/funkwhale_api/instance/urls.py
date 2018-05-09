from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^nodeinfo/2.0/$', views.NodeInfo.as_view(), name='nodeinfo-2.0'),
    url(r'^settings/$', views.InstanceSettings.as_view(), name='settings'),
]
