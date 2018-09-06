import io
import os

import pytest
from django.urls import reverse
from django.utils import timezone

from funkwhale_api.music import serializers, tasks, views

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def test_artist_list_serializer(api_request, factories, logged_in_api_client):
    track = factories["music.TrackFile"](library__privacy_level="everyone").track
    artist = track.artist
    request = api_request.get("/")
    qs = artist.__class__.objects.with_albums()
    serializer = serializers.ArtistWithAlbumsSerializer(
        qs, many=True, context={"request": request}
    )
    expected = {"count": 1, "next": None, "previous": None, "results": serializer.data}
    url = reverse("api:v1:artists-list")
    response = logged_in_api_client.get(url)

    assert response.status_code == 200
    assert response.data == expected


def test_album_list_serializer(api_request, factories, logged_in_api_client):
    track = factories["music.TrackFile"](library__privacy_level="everyone").track
    album = track.album
    request = api_request.get("/")
    qs = album.__class__.objects.all()
    serializer = serializers.AlbumSerializer(
        qs, many=True, context={"request": request}
    )
    expected = {"count": 1, "next": None, "previous": None, "results": serializer.data}
    expected["results"][0]["is_playable"] = True
    expected["results"][0]["tracks"][0]["is_playable"] = True
    url = reverse("api:v1:albums-list")
    response = logged_in_api_client.get(url)

    assert response.status_code == 200
    assert response.data["results"][0] == expected["results"][0]


def test_track_list_serializer(api_request, factories, logged_in_api_client):
    track = factories["music.TrackFile"](library__privacy_level="everyone").track
    request = api_request.get("/")
    qs = track.__class__.objects.all()
    serializer = serializers.TrackSerializer(
        qs, many=True, context={"request": request}
    )
    expected = {"count": 1, "next": None, "previous": None, "results": serializer.data}
    expected["results"][0]["is_playable"] = True
    url = reverse("api:v1:tracks-list")
    response = logged_in_api_client.get(url)

    assert response.status_code == 200
    assert response.data == expected


@pytest.mark.parametrize("param,expected", [("true", "full"), ("false", "empty")])
def test_artist_view_filter_playable(param, expected, factories, api_request):
    artists = {
        "empty": factories["music.Artist"](),
        "full": factories["music.TrackFile"](
            library__privacy_level="everyone"
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
        "full": factories["music.TrackFile"](
            library__privacy_level="everyone"
        ).track.album,
    }

    request = api_request.get("/", {"playable": param})
    view = views.AlbumViewSet()
    view.action_map = {"get": "list"}
    expected = [artists[expected]]
    view.request = view.initialize_request(request)
    queryset = view.filter_queryset(view.get_queryset())

    assert list(queryset) == expected


def test_can_serve_track_file_as_remote_library(
    factories, authenticated_actor, logged_in_api_client, settings, preferences
):
    preferences["common__api_authentication_required"] = True
    track_file = factories["music.TrackFile"](library__privacy_level="everyone")
    library_actor = track_file.library.actor
    factories["federation.Follow"](
        approved=True, actor=authenticated_actor, target=library_actor
    )

    response = logged_in_api_client.get(track_file.track.listen_url)

    assert response.status_code == 200
    assert response["X-Accel-Redirect"] == "{}{}".format(
        settings.PROTECT_FILES_PATH, track_file.audio_file.url
    )


def test_can_serve_track_file_as_remote_library_deny_not_following(
    factories, authenticated_actor, settings, api_client, preferences
):
    preferences["common__api_authentication_required"] = True
    track_file = factories["music.TrackFile"](library__privacy_level="everyone")
    response = api_client.get(track_file.track.listen_url)

    assert response.status_code == 403


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
    tf = factories["music.TrackFile"](
        in_place=True,
        source="file:///app/music/hello/world.mp3",
        library__privacy_level="everyone",
    )
    response = api_client.get(tf.track.listen_url)

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

    tf = factories["music.TrackFile"](library__privacy_level="everyone")
    tf.__class__.objects.filter(pk=tf.pk).update(audio_file="tracks/hello/world.mp3")
    response = api_client.get(tf.track.listen_url)

    assert response.status_code == 200
    assert response[headers[proxy]] == expected


def test_can_proxy_remote_track(factories, settings, api_client, r_mock, preferences):
    preferences["common__api_authentication_required"] = False
    url = "https://file.test"
    track_file = factories["music.TrackFile"](
        library__privacy_level="everyone", audio_file="", source=url
    )

    r_mock.get(url, body=io.BytesIO(b"test"))
    response = api_client.get(track_file.track.listen_url)
    track_file.refresh_from_db()

    assert response.status_code == 200
    assert response["X-Accel-Redirect"] == "{}{}".format(
        settings.PROTECT_FILES_PATH, track_file.audio_file.url
    )
    assert track_file.audio_file.read() == b"test"


def test_serve_updates_access_date(factories, settings, api_client, preferences):
    preferences["common__api_authentication_required"] = False
    track_file = factories["music.TrackFile"](library__privacy_level="everyone")
    now = timezone.now()
    assert track_file.accessed_date is None

    response = api_client.get(track_file.track.listen_url)
    track_file.refresh_from_db()

    assert response.status_code == 200
    assert track_file.accessed_date > now


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
    tf = factories["music.TrackFile"]()
    url = reverse("api:v1:listen-detail", kwargs={"uuid": tf.track.uuid})
    response = logged_in_api_client.get(url)

    assert response.status_code == 404


def test_listen_correct_access(factories, logged_in_api_client):
    logged_in_api_client.user.create_actor()
    tf = factories["music.TrackFile"](
        library__actor=logged_in_api_client.user.actor, library__privacy_level="me"
    )
    url = reverse("api:v1:listen-detail", kwargs={"uuid": tf.track.uuid})
    response = logged_in_api_client.get(url)

    assert response.status_code == 200


def test_listen_explicit_file(factories, logged_in_api_client, mocker):
    mocked_serve = mocker.spy(views, "handle_serve")
    tf1 = factories["music.TrackFile"](library__privacy_level="everyone")
    tf2 = factories["music.TrackFile"](
        library__privacy_level="everyone", track=tf1.track
    )
    url = reverse("api:v1:listen-detail", kwargs={"uuid": tf2.track.uuid})
    response = logged_in_api_client.get(url, {"file": tf2.uuid})

    assert response.status_code == 200
    mocked_serve.assert_called_once_with(tf2, user=logged_in_api_client.user)


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


def test_user_cannot_get_other_actors_files(factories, logged_in_api_client):
    logged_in_api_client.user.create_actor()
    track_file = factories["music.TrackFile"]()

    url = reverse("api:v1:trackfiles-detail", kwargs={"uuid": track_file.uuid})
    response = logged_in_api_client.get(url)

    assert response.status_code == 404


def test_user_cannot_delete_other_actors_files(factories, logged_in_api_client):
    logged_in_api_client.user.create_actor()
    track_file = factories["music.TrackFile"]()

    url = reverse("api:v1:trackfiles-detail", kwargs={"uuid": track_file.uuid})
    response = logged_in_api_client.delete(url)

    assert response.status_code == 404


def test_user_cannot_list_other_actors_files(factories, logged_in_api_client):
    logged_in_api_client.user.create_actor()
    factories["music.TrackFile"]()

    url = reverse("api:v1:trackfiles-list")
    response = logged_in_api_client.get(url)

    assert response.status_code == 200
    assert response.data["count"] == 0


def test_user_can_create_track_file(
    logged_in_api_client, factories, mocker, audio_file
):
    library = factories["music.Library"](actor__user=logged_in_api_client.user)
    url = reverse("api:v1:trackfiles-list")
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

    tf = library.files.latest("id")

    audio_file.seek(0)
    assert tf.audio_file.read() == audio_file.read()
    assert tf.source == "upload://test"
    assert tf.import_reference == "test"
    assert tf.track is None
    m.assert_called_once_with(tasks.import_track_file.delay, track_file_id=tf.pk)
