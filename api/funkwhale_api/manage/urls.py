from django.conf.urls import include, url
from rest_framework import routers

from . import views

federation_router = routers.SimpleRouter()
federation_router.register(r"domains", views.ManageDomainViewSet, "domains")

library_router = routers.SimpleRouter()
library_router.register(r"albums", views.ManageAlbumViewSet, "albums")
library_router.register(r"artists", views.ManageArtistViewSet, "artists")
library_router.register(r"libraries", views.ManageLibraryViewSet, "libraries")
library_router.register(r"tracks", views.ManageTrackViewSet, "tracks")
library_router.register(r"uploads", views.ManageUploadViewSet, "uploads")

moderation_router = routers.SimpleRouter()
moderation_router.register(
    r"instance-policies", views.ManageInstancePolicyViewSet, "instance-policies"
)

users_router = routers.SimpleRouter()
users_router.register(r"users", views.ManageUserViewSet, "users")
users_router.register(r"invitations", views.ManageInvitationViewSet, "invitations")

other_router = routers.SimpleRouter()
other_router.register(r"accounts", views.ManageActorViewSet, "accounts")

urlpatterns = [
    url(
        r"^federation/",
        include((federation_router.urls, "federation"), namespace="federation"),
    ),
    url(r"^library/", include((library_router.urls, "instance"), namespace="library")),
    url(
        r"^moderation/",
        include((moderation_router.urls, "moderation"), namespace="moderation"),
    ),
    url(r"^users/", include((users_router.urls, "instance"), namespace="users")),
] + other_router.urls
