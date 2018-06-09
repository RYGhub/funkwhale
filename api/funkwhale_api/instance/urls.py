from django.conf.urls import url
from rest_framework import routers

from . import views

admin_router = routers.SimpleRouter()
admin_router.register(r"admin/settings", views.AdminSettings, "admin-settings")

urlpatterns = [
    url(r"^nodeinfo/2.0/$", views.NodeInfo.as_view(), name="nodeinfo-2.0"),
    url(r"^settings/$", views.InstanceSettings.as_view(), name="settings"),
] + admin_router.urls
