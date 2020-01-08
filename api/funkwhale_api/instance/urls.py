from django.conf.urls import url
from funkwhale_api.common import routers

from . import views

admin_router = routers.OptionalSlashRouter()
admin_router.register(r"admin/settings", views.AdminSettings, "admin-settings")

urlpatterns = [
    url(r"^nodeinfo/2.0/?$", views.NodeInfo.as_view(), name="nodeinfo-2.0"),
    url(r"^settings/?$", views.InstanceSettings.as_view(), name="settings"),
    url(r"^spa-manifest.json", views.SpaManifest.as_view(), name="spa-manifest"),
] + admin_router.urls
