from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^nodeinfo/$', views.NodeInfo.as_view(), name='nodeinfo'),
    url(r'^settings/$', views.InstanceSettings.as_view(), name='settings'),
]
