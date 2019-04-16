import io
import magic
import os

import pytest
from django.urls import reverse
from django.utils import timezone

from funkwhale_api.common import utils
from funkwhale_api.federation import api_serializers as federation_api_serializers
from funkwhale_api.federation import utils as federation_utils
from funkwhale_api.music import licenses, models, serializers, tasks, views

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def test_artist_list_serializer(api_request, factories, logged_in_api_client):
    track = factories["music.Upload"](
        library__privacy_level="everyone", import_status="finished"
    ).track
    artist = track.artist
    request = api_request.get("/")
    qs = artist.__class__.objects.with_albums()
    serializer = serializers.ArtistWithAlbumsSerializer(
        qs, many=True, context={"request": request}
    )
    expected = {"count": 1, "next": None, "previous": None, "results": serializer.data}
    for artist in serializer.data:
        for album in artist["albums"]:
            album["is_playable"] = True
    url = reverse("api:v1:artists-list")
    response = logged_in_api_client.get(url)

    assert response.status_code == 200
    assert response.data == expected


def test_album_list_serializer(api_request, factories, logged_in_api_client):
    track = factories["music.Upload"](
        library__privacy_level="everyone", import_status="finished"
    ).track
    album = track.album
    request = api_request.get("/")
    qs = album.__class__.objects.with_prefetched_tracks_and_playable_uploads(None)
    serializer = serializers.AlbumSerializer(
        qs, many=True, context={"request": request}
    )
    expected = {"count": 1, "next": None, "previous": None, "results": serializer.data}
    url = reverse("api:v1:albums-list")
    response = logged_in_api_client.get(url)

    assert response.status_code == 200
    assert response.data["results"][0] == expected["results"][0]


def test_track_list_serializer(api_request, factories, logged_in_api_client):
    track = factories["music.Upload"](
        library__privacy_level="everyone", import_status="finished"
    ).track
    request = api_request.get("/")
    qs = track.__class__.objects.with_playable_uploads(None)
    serializer = serializers.TrackSerializer(
        qs, many=True, context={"request": request}
    )
    expected = {"count": 1, "next": None, "previous": None, "results": serializer.data}
    url = reverse("api:v1:tracks-list")
    response = logged_in_api_client.get(url)

    assert response.status_code == 200
    assert response.data == expected


def test_track_list_filter_id(api_request, factories, logged_in_api_client):
    track1 = factories["music.Track"]()
    track2 = factories["music.Track"]()
    factories["music.Track"]()
    url = reverse("api:v1:tracks-list")
    response = logged_in_api_client.get(url, {"id[]": [track1.id, track2.id]})

    assert response.status_code == 200
    assert response.data["count"] == 2
    assert response.data["results"][0]["id"] == track2.id
    assert response.data["results"][1]["id"] == track1.id


@pytest.mark.parametrize("param,expected", [("true", "full"), ("false", "empty")])
def test_artist_view_filter_playable(param, expected, factories, api_request):
    artists = {
        "empty": factories["music.Artist"](),
        "full": factories["music.Upload"](
            library__privacy_level="everyone", import_status="finished"
        ).track.artist,
    }

    request = api_request.get("/", {"playable": param})
    view = views.ArtistViewSet()
    view.action_map = {"get": "list"}
    expected = [artists[expected]]
    view.request = view.initialize_request(request)
    queryset = view.filter_queryset(view.get_queryset())

    assert list(queryset) == expected


@pytest.mark.parametrize("param,expected", [("true", "full"), ("false", "empty")])
def test_album_view_filter_playable(param, expected, factories, api_request):
    artists = {
        "empty": factories["music.Album"](),
        "full": factories["music.Upload"](
            library__privacy_level="everyone", import_status="finished"
        ).track.album,
    }

    request = api_request.get("/", {"playable": param})
    view = views.AlbumViewSet()
    view.action_map = {"get": "list"}
    expected = [artists[expected]]
    view.request = view.initialize_request(request)
    queryset = view.filter_queryset(view.get_queryset())

    assert list(queryset) == expected


@pytest.mark.parametrize(
    "param", [("I've Got"), ("Français"), ("I've Got Everything : Spoken Word Poetry")]
)
def test_album_view_filter_query(param, factories, api_request):
    # Test both partial and full search.
    factories["music.Album"](title="I've Got Nothing : Original Soundtrack")
    factories["music.Album"](title="I've Got Cake : Remix")
    factories["music.Album"](title="Français Et Tu")
    factories["music.Album"](title="I've Got Everything : Spoken Word Poetry")

    request = api_request.get("/", {"q": param})
    view = views.AlbumViewSet()
    view.action_map = {"get": "list"}
    view.request = view.initialize_request(request)
    queryset = view.filter_queryset(view.get_queryset())

    # Loop through our "expected list", and assert some string finds against our param.
    for val in list(queryset):
        assert val.title.find(param) != -1


def test_can_serve_upload_as_remote_library(
    factories, authenticated_actor, logged_in_api_client, settings, preferences
):
    preferences["common__api_authentication_required"] = True
    upload = factories["music.Upload"](
        library__privacy_level="everyone", import_status="finished"
    )
    library_actor = upload.library.actor
    factories["federation.Follow"](
        approved=True, actor=authenticated_actor, target=library_actor
    )

    response = logged_in_api_client.get(upload.track.listen_url)

    assert response.status_code == 200
    assert response["X-Accel-Redirect"] == "{}{}".format(
        settings.PROTECT_FILES_PATH, upload.audio_file.url
    )


def test_can_serve_upload_as_remote_library_deny_not_following(
    factories, authenticated_actor, settings, api_client, preferences
):
    preferences["common__api_authentication_required"] = True
    upload = factories["music.Upload"](
        import_status="finished", library__privacy_level="instance"
    )
    response = api_client.get(upload.track.listen_url)

    assert response.status_code == 404


@pytest.mark.parametrize(
    "proxy,serve_path,expected",
    [
        ("apache2", "/host/music", "/host/music/hello/world.mp3"),
        ("apache2", "/app/music", "/app/music/hello/world.mp3"),
        ("nginx", "/host/music", "/_protected/music/hello/world.mp3"),
        ("nginx", "/app/music", "/_protected/music/hello/world.mp3"),
    ],
)
def test_serve_file_in_place(
    proxy, serve_path, expected, factories, api_client, preferences, settings
):
    headers = {"apache2": "X-Sendfile", "nginx": "X-Accel-Redirect"}
    preferences["common__api_authentication_required"] = False
    settings.PROTECT_FILE_PATH = "/_protected/music"
    settings.REVERSE_PROXY_TYPE = proxy
    settings.MUSIC_DIRECTORY_PATH = "/app/music"
    settings.MUSIC_DIRECTORY_SERVE_PATH = serve_path
    upload = factories["music.Upload"](
        in_place=True,
        import_status="finished",
        source="file:///app/music/hello/world.mp3",
        library__privacy_level="everyone",
    )
    response = api_client.get(upload.track.listen_url)

    assert response.status_code == 200
    assert response[headers[proxy]] == expected


@pytest.mark.parametrize(
    "proxy,serve_path,expected",
    [
        ("apache2", "/host/music", "/host/music/hello/worldéà.mp3"),
        ("apache2", "/app/music", "/app/music/hello/worldéà.mp3"),
        ("nginx", "/host/music", "/_protected/music/hello/worldéà.mp3"),
        ("nginx", "/app/music", "/_protected/music/hello/worldéà.mp3"),
    ],
)
def test_serve_file_in_place_utf8(
    proxy, serve_path, expected, factories, api_client, settings, preferences
):
    preferences["common__api_authentication_required"] = False
    settings.PROTECT_FILE_PATH = "/_protected/music"
    settings.REVERSE_PROXY_TYPE = proxy
    settings.MUSIC_DIRECTORY_PATH = "/app/music"
    settings.MUSIC_DIRECTORY_SERVE_PATH = serve_path
    path = views.get_file_path("/app/music/hello/worldéà.mp3")

    assert path == expected.encode("utf-8")


@pytest.mark.parametrize(
    "proxy,serve_path,expected",
    [
        ("apache2", "/host/music", "/host/media/tracks/hello/world.mp3"),
        # apache with container not supported yet
        # ('apache2', '/app/music', '/app/music/tracks/hello/world.mp3'),
        ("nginx", "/host/music", "/_protected/media/tracks/hello/world.mp3"),
        ("nginx", "/app/music", "/_protected/media/tracks/hello/world.mp3"),
    ],
)
def test_serve_file_media(
    proxy, serve_path, expected, factories, api_client, settings, preferences
):
    headers = {"apache2": "X-Sendfile", "nginx": "X-Accel-Redirect"}
    preferences["common__api_authentication_required"] = False
    settings.MEDIA_ROOT = "/host/media"
    settings.PROTECT_FILE_PATH = "/_protected/music"
    settings.REVERSE_PROXY_TYPE = proxy
    settings.MUSIC_DIRECTORY_PATH = "/app/music"
    settings.MUSIC_DIRECTORY_SERVE_PATH = serve_path

    upload = factories["music.Upload"](
        library__privacy_level="everyone", import_status="finished"
    )
    upload.__class__.objects.filter(pk=upload.pk).update(
        audio_file="tracks/hello/world.mp3"
    )
    response = api_client.get(upload.track.listen_url)

    assert response.status_code == 200
    assert response[headers[proxy]] == expected


def test_can_proxy_remote_track(factories, settings, api_client, r_mock, preferences):
    preferences["common__api_authentication_required"] = False
    url = "https://file.test"
    upload = factories["music.Upload"](
        library__privacy_level="everyone",
        audio_file="",
        source=url,
        import_status="finished",
    )

    r_mock.get(url, body=io.BytesIO(b"test"))
    response = api_client.get(upload.track.listen_url)
    upload.refresh_from_db()

    assert response.status_code == 200
    assert response["X-Accel-Redirect"] == "{}{}".format(
        settings.PROTECT_FILES_PATH, upload.audio_file.url
    )
    assert upload.audio_file.read() == b"test"


def test_serve_updates_access_date(factories, settings, api_client, preferences):
    preferences["common__api_authentication_required"] = False
    upload = factories["music.Upload"](
        library__privacy_level="everyone", import_status="finished"
    )
    now = timezone.now()
    assert upload.accessed_date is None

    response = api_client.get(upload.track.listen_url)
    upload.refresh_from_db()

    assert response.status_code == 200
    assert upload.accessed_date > now


def test_listen_no_track(factories, logged_in_api_client):
    url = reverse("api:v1:listen-detail", kwargs={"uuid": "noop"})
    response = logged_in_api_client.get(url)

    assert response.status_code == 404


def test_listen_no_file(factories, logged_in_api_client):
    track = factories["music.Track"]()
    url = reverse("api:v1:listen-detail", kwargs={"uuid": track.uuid})
    response = logged_in_api_client.get(url)

    assert response.status_code == 404


def test_listen_no_available_file(factories, logged_in_api_client):
    upload = factories["music.Upload"]()
    url = reverse("api:v1:listen-detail", kwargs={"uuid": upload.track.uuid})
    response = logged_in_api_client.get(url)

    assert response.status_code == 404


def test_listen_correct_access(factories, logged_in_api_client):
    logged_in_api_client.user.create_actor()
    upload = factories["music.Upload"](
        library__actor=logged_in_api_client.user.actor,
        library__privacy_level="me",
        import_status="finished",
    )
    url = reverse("api:v1:listen-detail", kwargs={"uuid": upload.track.uuid})
    response = logged_in_api_client.get(url)

    assert response.status_code == 200


def test_listen_explicit_file(factories, logged_in_api_client, mocker):
    mocked_serve = mocker.spy(views, "handle_serve")
    upload1 = factories["music.Upload"](
        library__privacy_level="everyone", import_status="finished"
    )
    upload2 = factories["music.Upload"](
        library__privacy_level="everyone", track=upload1.track, import_status="finished"
    )
    url = reverse("api:v1:listen-detail", kwargs={"uuid": upload2.track.uuid})
    response = logged_in_api_client.get(url, {"upload": upload2.uuid})

    assert response.status_code == 200
    mocked_serve.assert_called_once_with(
        upload2, user=logged_in_api_client.user, format=None, max_bitrate=None
    )


@pytest.mark.parametrize(
    "mimetype,format,expected",
    [
        # already in proper format
        ("audio/mpeg", "mp3", False),
        # empty mimetype / format
        (None, "mp3", False),
        ("audio/mpeg", None, False),
        # unsupported format
        ("audio/mpeg", "noop", False),
        # should transcode
        ("audio/mpeg", "ogg", True),
    ],
)
def test_should_transcode(mimetype, format, expected, factories):
    upload = models.Upload(mimetype=mimetype)
    assert views.should_transcode(upload, format) is expected


@pytest.mark.parametrize(
    "bitrate,max_bitrate,expected",
    [
        # already in acceptable bitrate
        (192000, 320000, False),
        # No max bitrate specified
        (192000, None, False),
        # requested max below available
        (192000, 128000, True),
    ],
)
def test_should_transcode_bitrate(bitrate, max_bitrate, expected, factories):
    upload = models.Upload(mimetype="audio/mpeg", bitrate=bitrate)
    assert views.should_transcode(upload, "mp3", max_bitrate=max_bitrate) is expected


@pytest.mark.parametrize("value", [True, False])
def test_should_transcode_according_to_preference(value, preferences, factories):
    upload = models.Upload(mimetype="audio/ogg")
    expected = value
    preferences["music__transcoding_enabled"] = value

    assert views.should_transcode(upload, "mp3") is expected


def test_handle_serve_create_mp3_version(factories, now):
    user = factories["users.User"]()
    upload = factories["music.Upload"](bitrate=42)
    response = views.handle_serve(upload, user, format="mp3")

    version = upload.versions.latest("id")

    assert version.mimetype == "audio/mpeg"
    assert version.accessed_date == now
    assert version.bitrate == upload.bitrate
    assert version.audio_file.path.endswith(".mp3")
    assert version.size == version.audio_file.size
    assert magic.from_buffer(version.audio_file.read(), mime=True) == "audio/mpeg"

    assert response.status_code == 200


def test_listen_transcode(factories, now, logged_in_api_client, mocker):
    upload = factories["music.Upload"](
        import_status="finished", library__actor__user=logged_in_api_client.user
    )
    url = reverse("api:v1:listen-detail", kwargs={"uuid": upload.track.uuid})
    handle_serve = mocker.spy(views, "handle_serve")
    response = logged_in_api_client.get(url, {"to": "mp3"})

    assert response.status_code == 200

    handle_serve.assert_called_once_with(
        upload, user=logged_in_api_client.user, format="mp3", max_bitrate=None
    )


@pytest.mark.parametrize(
    "max_bitrate, expected",
    [
        ("", None),
        ("", None),
        ("-1", None),
        ("128", 128000),
        ("320", 320000),
        ("460", 320000),
    ],
)
def test_listen_transcode_bitrate(
    max_bitrate, expected, factories, now, logged_in_api_client, mocker
):
    upload = factories["music.Upload"](
        import_status="finished", library__actor__user=logged_in_api_client.user
    )
    url = reverse("api:v1:listen-detail", kwargs={"uuid": upload.track.uuid})
    handle_serve = mocker.spy(views, "handle_serve")
    response = logged_in_api_client.get(url, {"max_bitrate": max_bitrate})

    assert response.status_code == 200

    handle_serve.assert_called_once_with(
        upload, user=logged_in_api_client.user, format=None, max_bitrate=expected
    )


@pytest.mark.parametrize("serve_path", [("/host/music",), ("/app/music",)])
def test_listen_transcode_in_place(
    serve_path, factories, now, logged_in_api_client, mocker, settings
):
    settings.MUSIC_DIRECTORY_PATH = "/app/music"
    settings.MUSIC_DIRECTORY_SERVE_PATH = serve_path
    upload = factories["music.Upload"](
        import_status="finished",
        library__actor__user=logged_in_api_client.user,
        audio_file=None,
        source="file://" + os.path.join(DATA_DIR, "test.ogg"),
    )

    assert upload.get_audio_segment()

    url = reverse("api:v1:listen-detail", kwargs={"uuid": upload.track.uuid})
    handle_serve = mocker.spy(views, "handle_serve")
    response = logged_in_api_client.get(url, {"to": "mp3"})

    assert response.status_code == 200

    handle_serve.assert_called_once_with(
        upload, user=logged_in_api_client.user, format="mp3", max_bitrate=None
    )


def test_user_can_create_library(factories, logged_in_api_client):
    actor = logged_in_api_client.user.create_actor()
    url = reverse("api:v1:libraries-list")

    response = logged_in_api_client.post(
        url, {"name": "hello", "description": "world", "privacy_level": "me"}
    )
    library = actor.libraries.first()

    assert response.status_code == 201

    assert library.actor == actor
    assert library.name == "hello"
    assert library.description == "world"
    assert library.privacy_level == "me"
    assert library.fid == library.get_federation_id()
    assert library.followers_url == library.fid + "/followers"


def test_user_can_list_their_library(factories, logged_in_api_client):
    actor = logged_in_api_client.user.create_actor()
    library = factories["music.Library"](actor=actor)
    factories["music.Library"]()

    url = reverse("api:v1:libraries-list")
    response = logged_in_api_client.get(url)

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["uuid"] == str(library.uuid)


def test_user_cannot_delete_other_actors_library(factories, logged_in_api_client):
    logged_in_api_client.user.create_actor()
    library = factories["music.Library"](privacy_level="everyone")

    url = reverse("api:v1:libraries-detail", kwargs={"uuid": library.uuid})
    response = logged_in_api_client.delete(url)

    assert response.status_code == 404


def test_library_delete_via_api_triggers_outbox(factories, mocker):
    dispatch = mocker.patch("funkwhale_api.federation.routes.outbox.dispatch")
    library = factories["music.Library"]()
    view = views.LibraryViewSet()
    view.perform_destroy(library)
    dispatch.assert_called_once_with(
        {"type": "Delete", "object": {"type": "Library"}}, context={"library": library}
    )


def test_user_cannot_get_other_actors_uploads(factories, logged_in_api_client):
    logged_in_api_client.user.create_actor()
    upload = factories["music.Upload"]()

    url = reverse("api:v1:uploads-detail", kwargs={"uuid": upload.uuid})
    response = logged_in_api_client.get(url)

    assert response.status_code == 404


def test_user_cannot_delete_other_actors_uploads(factories, logged_in_api_client):
    logged_in_api_client.user.create_actor()
    upload = factories["music.Upload"]()

    url = reverse("api:v1:uploads-detail", kwargs={"uuid": upload.uuid})
    response = logged_in_api_client.delete(url)

    assert response.status_code == 404


def test_upload_delete_via_api_triggers_outbox(factories, mocker):
    dispatch = mocker.patch("funkwhale_api.federation.routes.outbox.dispatch")
    upload = factories["music.Upload"]()
    view = views.UploadViewSet()
    view.perform_destroy(upload)
    dispatch.assert_called_once_with(
        {"type": "Delete", "object": {"type": "Audio"}}, context={"uploads": [upload]}
    )


def test_user_cannot_list_other_actors_uploads(factories, logged_in_api_client):
    logged_in_api_client.user.create_actor()
    factories["music.Upload"]()

    url = reverse("api:v1:uploads-list")
    response = logged_in_api_client.get(url)

    assert response.status_code == 200
    assert response.data["count"] == 0


def test_user_can_create_upload(logged_in_api_client, factories, mocker, audio_file):
    library = factories["music.Library"](actor__user=logged_in_api_client.user)
    url = reverse("api:v1:uploads-list")
    m = mocker.patch("funkwhale_api.common.utils.on_commit")

    response = logged_in_api_client.post(
        url,
        {
            "audio_file": audio_file,
            "source": "upload://test",
            "import_reference": "test",
            "library": library.uuid,
        },
    )

    assert response.status_code == 201

    upload = library.uploads.latest("id")

    audio_file.seek(0)
    assert upload.audio_file.read() == audio_file.read()
    assert upload.source == "upload://test"
    assert upload.import_reference == "test"
    assert upload.track is None
    m.assert_called_once_with(tasks.process_upload.delay, upload_id=upload.pk)


def test_user_can_list_own_library_follows(factories, logged_in_api_client):
    actor = logged_in_api_client.user.create_actor()
    library = factories["music.Library"](actor=actor)
    another_library = factories["music.Library"](actor=actor)
    follow = factories["federation.LibraryFollow"](target=library)
    factories["federation.LibraryFollow"](target=another_library)

    url = reverse("api:v1:libraries-follows", kwargs={"uuid": library.uuid})

    response = logged_in_api_client.get(url)

    assert response.data == {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [federation_api_serializers.LibraryFollowSerializer(follow).data],
    }


@pytest.mark.parametrize("entity", ["artist", "album", "track"])
def test_can_get_libraries_for_music_entities(
    factories, api_client, entity, preferences
):
    preferences["common__api_authentication_required"] = False
    upload = factories["music.Upload"](playable=True)
    # another private library that should not appear
    factories["music.Upload"](
        import_status="finished", library__privacy_level="me", track=upload.track
    ).library
    library = upload.library
    setattr(library, "_uploads_count", 1)
    data = {
        "artist": upload.track.artist,
        "album": upload.track.album,
        "track": upload.track,
    }

    url = reverse("api:v1:{}s-libraries".format(entity), kwargs={"pk": data[entity].pk})

    response = api_client.get(url)
    expected = federation_api_serializers.LibrarySerializer(library).data

    assert response.status_code == 200
    assert response.data == {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [expected],
    }


def test_list_licenses(api_client, preferences, mocker):
    licenses.load(licenses.LICENSES)
    load = mocker.spy(licenses, "load")
    preferences["common__api_authentication_required"] = False

    expected = [
        serializers.LicenseSerializer(l.conf).data
        for l in models.License.objects.order_by("code")
    ]
    url = reverse("api:v1:licenses-list")

    response = api_client.get(url)

    assert response.data["results"] == expected
    load.assert_called_once_with(licenses.LICENSES)


def test_detail_license(api_client, preferences):
    preferences["common__api_authentication_required"] = False
    id = "cc-by-sa-4.0"
    expected = serializers.LicenseSerializer(licenses.LICENSES_BY_ID[id]).data

    url = reverse("api:v1:licenses-detail", kwargs={"pk": id})

    response = api_client.get(url)

    assert response.data == expected


def test_oembed_track(factories, no_api_auth, api_client, settings):
    settings.FUNKWHALE_URL = "http://test"
    settings.FUNKWHALE_EMBED_URL = "http://embed"
    track = factories["music.Track"]()
    url = reverse("api:v1:oembed")
    track_url = "https://test.com/library/tracks/{}".format(track.pk)
    iframe_src = "http://embed?type=track&id={}".format(track.pk)
    expected = {
        "version": "1.0",
        "type": "rich",
        "provider_name": settings.APP_NAME,
        "provider_url": settings.FUNKWHALE_URL,
        "height": 150,
        "width": 600,
        "title": "{} by {}".format(track.title, track.artist.name),
        "description": track.full_name,
        "thumbnail_url": federation_utils.full_url(
            track.album.cover.crop["400x400"].url
        ),
        "thumbnail_height": 400,
        "thumbnail_width": 400,
        "html": '<iframe width="600" height="150" scrolling="no" frameborder="no" src="{}"></iframe>'.format(
            iframe_src
        ),
        "author_name": track.artist.name,
        "author_url": federation_utils.full_url(
            utils.spa_reverse("library_artist", kwargs={"pk": track.artist.pk})
        ),
    }

    response = api_client.get(url, {"url": track_url, "format": "json"})

    assert response.data == expected


def test_oembed_album(factories, no_api_auth, api_client, settings):
    settings.FUNKWHALE_URL = "http://test"
    settings.FUNKWHALE_EMBED_URL = "http://embed"
    track = factories["music.Track"]()
    album = track.album
    url = reverse("api:v1:oembed")
    album_url = "https://test.com/library/albums/{}".format(album.pk)
    iframe_src = "http://embed?type=album&id={}".format(album.pk)
    expected = {
        "version": "1.0",
        "type": "rich",
        "provider_name": settings.APP_NAME,
        "provider_url": settings.FUNKWHALE_URL,
        "height": 400,
        "width": 600,
        "title": "{} by {}".format(album.title, album.artist.name),
        "description": "{} by {}".format(album.title, album.artist.name),
        "thumbnail_url": federation_utils.full_url(album.cover.crop["400x400"].url),
        "thumbnail_height": 400,
        "thumbnail_width": 400,
        "html": '<iframe width="600" height="400" scrolling="no" frameborder="no" src="{}"></iframe>'.format(
            iframe_src
        ),
        "author_name": album.artist.name,
        "author_url": federation_utils.full_url(
            utils.spa_reverse("library_artist", kwargs={"pk": album.artist.pk})
        ),
    }

    response = api_client.get(url, {"url": album_url, "format": "json"})

    assert response.data == expected


def test_oembed_artist(factories, no_api_auth, api_client, settings):
    settings.FUNKWHALE_URL = "http://test"
    settings.FUNKWHALE_EMBED_URL = "http://embed"
    track = factories["music.Track"]()
    album = track.album
    artist = track.artist
    url = reverse("api:v1:oembed")
    artist_url = "https://test.com/library/artists/{}".format(artist.pk)
    iframe_src = "http://embed?type=artist&id={}".format(artist.pk)
    expected = {
        "version": "1.0",
        "type": "rich",
        "provider_name": settings.APP_NAME,
        "provider_url": settings.FUNKWHALE_URL,
        "height": 400,
        "width": 600,
        "title": artist.name,
        "description": artist.name,
        "thumbnail_url": federation_utils.full_url(album.cover.crop["400x400"].url),
        "thumbnail_height": 400,
        "thumbnail_width": 400,
        "html": '<iframe width="600" height="400" scrolling="no" frameborder="no" src="{}"></iframe>'.format(
            iframe_src
        ),
        "author_name": artist.name,
        "author_url": federation_utils.full_url(
            utils.spa_reverse("library_artist", kwargs={"pk": artist.pk})
        ),
    }

    response = api_client.get(url, {"url": artist_url, "format": "json"})

    assert response.data == expected
