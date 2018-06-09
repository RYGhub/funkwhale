from django.conf.urls import include, url
from . import views

from rest_framework import routers

library_router = routers.SimpleRouter()
library_router.register(r"track-files", views.ManageTrackFileViewSet, "track-files")

urlpatterns = [
    url(r"^library/", include((library_router.urls, "instance"), namespace="library"))
]
