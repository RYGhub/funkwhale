from django.conf.urls import include, url
from funkwhale_api.common import routers

from . import views

federation_router = routers.OptionalSlashRouter()
federation_router.register(r"domains", views.ManageDomainViewSet, "domains")

library_router = routers.OptionalSlashRouter()
library_router.register(r"albums", views.ManageAlbumViewSet, "albums")
library_router.register(r"artists", views.ManageArtistViewSet, "artists")
library_router.register(r"libraries", views.ManageLibraryViewSet, "libraries")
library_router.register(r"tracks", views.ManageTrackViewSet, "tracks")
library_router.register(r"uploads", views.ManageUploadViewSet, "uploads")

moderation_router = routers.OptionalSlashRouter()
moderation_router.register(
    r"instance-policies", views.ManageInstancePolicyViewSet, "instance-policies"
)
moderation_router.register(r"reports", views.ManageReportViewSet, "reports")
moderation_router.register(r"requests", views.ManageUserRequestViewSet, "requests")
moderation_router.register(r"notes", views.ManageNoteViewSet, "notes")

users_router = routers.OptionalSlashRouter()
users_router.register(r"users", views.ManageUserViewSet, "users")
users_router.register(r"invitations", views.ManageInvitationViewSet, "invitations")

other_router = routers.OptionalSlashRouter()
other_router.register(r"accounts", views.ManageActorViewSet, "accounts")
other_router.register(r"channels", views.ManageChannelViewSet, "channels")
other_router.register(r"tags", views.ManageTagViewSet, "tags")

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
