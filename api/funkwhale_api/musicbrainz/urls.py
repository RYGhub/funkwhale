from django.conf.urls import url
from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register(r"search", views.SearchViewSet, "search")
urlpatterns = [
    url(
        "releases/(?P<uuid>[0-9a-z-]+)/$",
        views.ReleaseDetail.as_view(),
        name="release-detail",
    ),
    url(
        "artists/(?P<uuid>[0-9a-z-]+)/$",
        views.ArtistDetail.as_view(),
        name="artist-detail",
    ),
    url(
        "release-groups/browse/(?P<artist_uuid>[0-9a-z-]+)/$",
        views.ReleaseGroupBrowse.as_view(),
        name="release-group-browse",
    ),
    url(
        "releases/browse/(?P<release_group_uuid>[0-9a-z-]+)/$",
        views.ReleaseBrowse.as_view(),
        name="release-browse",
    ),
    # url('release-groups/(?P<uuid>[0-9a-z-]+)/$',
    #     views.ReleaseGroupDetail.as_view(),
    #     name='release-group-detail'),
] + router.urls
