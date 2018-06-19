from django.conf.urls import include, url
from rest_framework import routers

from . import views

library_router = routers.SimpleRouter()
library_router.register(r"track-files", views.ManageTrackFileViewSet, "track-files")
users_router = routers.SimpleRouter()
users_router.register(r"users", views.ManageUserViewSet, "users")

urlpatterns = [
    url(r"^library/", include((library_router.urls, "instance"), namespace="library")),
    url(r"^users/", include((users_router.urls, "instance"), namespace="users")),
]
