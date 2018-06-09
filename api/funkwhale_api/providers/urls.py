from django.conf.urls import include, url
from funkwhale_api.music import views

urlpatterns = [
    url(
        r"^youtube/",
        include(
            ("funkwhale_api.providers.youtube.urls", "youtube"), namespace="youtube"
        ),
    ),
    url(
        r"^musicbrainz/",
        include(
            ("funkwhale_api.musicbrainz.urls", "musicbrainz"), namespace="musicbrainz"
        ),
    ),
]
