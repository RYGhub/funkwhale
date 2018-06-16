from django.conf.urls import include, url
from rest_framework import routers

from . import views

library_router = routers.SimpleRouter()
library_router.register(r"track-files", views.ManageTrackFileViewSet, "track-files")

urlpatterns = [
    url(r"^library/", include((library_router.urls, "instance"), namespace="library"))
]
