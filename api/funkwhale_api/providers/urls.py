from django.conf.urls import include, url

urlpatterns = [
    url(
        r"^musicbrainz/",
        include(
            ("funkwhale_api.musicbrainz.urls", "musicbrainz"), namespace="musicbrainz"
        ),
    )
]
