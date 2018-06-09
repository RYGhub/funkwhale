import json
import pytest

from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone

from funkwhale_api.playlists import models
from funkwhale_api.playlists import serializers


def test_can_create_playlist_via_api(logged_in_api_client):
    url = reverse("api:v1:playlists-list")
    data = {"name": "test", "privacy_level": "everyone"}

    response = logged_in_api_client.post(url, data)

    playlist = logged_in_api_client.user.playlists.latest("id")
    assert playlist.name == "test"
    assert playlist.privacy_level == "everyone"


def test_serializer_includes_tracks_count(factories, logged_in_api_client):
    playlist = factories["playlists.Playlist"]()
    plt = factories["playlists.PlaylistTrack"](playlist=playlist)

    url = reverse("api:v1:playlists-detail", kwargs={"pk": playlist.pk})
    response = logged_in_api_client.get(url)

    assert response.data["tracks_count"] == 1


def test_playlist_inherits_user_privacy(logged_in_api_client):
    url = reverse("api:v1:playlists-list")
    user = logged_in_api_client.user
    user.privacy_level = "me"
    user.save()

    data = {"name": "test"}

    response = logged_in_api_client.post(url, data)
    playlist = user.playlists.latest("id")
    assert playlist.privacy_level == user.privacy_level


def test_can_add_playlist_track_via_api(factories, logged_in_api_client):
    tracks = factories["music.Track"].create_batch(5)
    playlist = factories["playlists.Playlist"](user=logged_in_api_client.user)
    url = reverse("api:v1:playlist-tracks-list")
    data = {"playlist": playlist.pk, "track": tracks[0].pk}

    response = logged_in_api_client.post(url, data)
    assert response.status_code == 201
    plts = logged_in_api_client.user.playlists.latest("id").playlist_tracks.all()
    assert plts.first().track == tracks[0]


@pytest.mark.parametrize(
    "name,method",
    [("api:v1:playlist-tracks-list", "post"), ("api:v1:playlists-list", "post")],
)
def test_url_requires_login(name, method, factories, api_client):
    url = reverse(name)

    response = getattr(api_client, method)(url, {})

    assert response.status_code == 401


def test_only_can_add_track_on_own_playlist_via_api(factories, logged_in_api_client):
    track = factories["music.Track"]()
    playlist = factories["playlists.Playlist"]()
    url = reverse("api:v1:playlist-tracks-list")
    data = {"playlist": playlist.pk, "track": track.pk}

    response = logged_in_api_client.post(url, data)
    assert response.status_code == 400
    assert playlist.playlist_tracks.count() == 0


def test_deleting_plt_updates_indexes(mocker, factories, logged_in_api_client):
    remove = mocker.spy(models.Playlist, "remove")
    track = factories["music.Track"]()
    plt = factories["playlists.PlaylistTrack"](
        index=0, playlist__user=logged_in_api_client.user
    )
    url = reverse("api:v1:playlist-tracks-detail", kwargs={"pk": plt.pk})

    response = logged_in_api_client.delete(url)

    assert response.status_code == 204
    remove.assert_called_once_with(plt.playlist, 0)


@pytest.mark.parametrize("level", ["instance", "me", "followers"])
def test_playlist_privacy_respected_in_list_anon(
    preferences, level, factories, api_client
):
    preferences["common__api_authentication_required"] = False
    factories["playlists.Playlist"](privacy_level=level)
    url = reverse("api:v1:playlists-list")
    response = api_client.get(url)

    assert response.data["count"] == 0


@pytest.mark.parametrize("method", ["PUT", "PATCH", "DELETE"])
def test_only_owner_can_edit_playlist(method, factories, logged_in_api_client):
    playlist = factories["playlists.Playlist"]()
    url = reverse("api:v1:playlists-detail", kwargs={"pk": playlist.pk})
    response = getattr(logged_in_api_client, method.lower())(url)

    assert response.status_code == 404


@pytest.mark.parametrize("method", ["PUT", "PATCH", "DELETE"])
def test_only_owner_can_edit_playlist_track(method, factories, logged_in_api_client):
    plt = factories["playlists.PlaylistTrack"]()
    url = reverse("api:v1:playlist-tracks-detail", kwargs={"pk": plt.pk})
    response = getattr(logged_in_api_client, method.lower())(url)

    assert response.status_code == 404


@pytest.mark.parametrize("level", ["instance", "me", "followers"])
def test_playlist_track_privacy_respected_in_list_anon(
    level, factories, api_client, preferences
):
    preferences["common__api_authentication_required"] = False
    factories["playlists.PlaylistTrack"](playlist__privacy_level=level)
    url = reverse("api:v1:playlist-tracks-list")
    response = api_client.get(url)

    assert response.data["count"] == 0


@pytest.mark.parametrize("level", ["instance", "me", "followers"])
def test_can_list_tracks_from_playlist(level, factories, logged_in_api_client):
    plt = factories["playlists.PlaylistTrack"](playlist__user=logged_in_api_client.user)
    url = reverse("api:v1:playlists-tracks", kwargs={"pk": plt.playlist.pk})
    response = logged_in_api_client.get(url)
    serialized_plt = serializers.PlaylistTrackSerializer(plt).data

    assert response.data["count"] == 1
    assert response.data["results"][0] == serialized_plt


def test_can_add_multiple_tracks_at_once_via_api(
    factories, mocker, logged_in_api_client
):
    playlist = factories["playlists.Playlist"](user=logged_in_api_client.user)
    tracks = factories["music.Track"].create_batch(size=5)
    track_ids = [t.id for t in tracks]
    mocker.spy(playlist, "insert_many")
    url = reverse("api:v1:playlists-add", kwargs={"pk": playlist.pk})
    response = logged_in_api_client.post(url, {"tracks": track_ids})

    assert response.status_code == 201
    assert playlist.playlist_tracks.count() == len(track_ids)

    for plt in playlist.playlist_tracks.order_by("index"):
        assert response.data["results"][plt.index]["id"] == plt.id
        assert plt.track == tracks[plt.index]


def test_can_clear_playlist_from_api(factories, mocker, logged_in_api_client):
    playlist = factories["playlists.Playlist"](user=logged_in_api_client.user)
    plts = factories["playlists.PlaylistTrack"].create_batch(size=5, playlist=playlist)
    url = reverse("api:v1:playlists-clear", kwargs={"pk": playlist.pk})
    response = logged_in_api_client.delete(url)

    assert response.status_code == 204
    assert playlist.playlist_tracks.count() == 0


def test_update_playlist_from_api(factories, mocker, logged_in_api_client):
    playlist = factories["playlists.Playlist"](user=logged_in_api_client.user)
    plts = factories["playlists.PlaylistTrack"].create_batch(size=5, playlist=playlist)
    url = reverse("api:v1:playlists-detail", kwargs={"pk": playlist.pk})
    response = logged_in_api_client.patch(url, {"name": "test"})
    playlist.refresh_from_db()

    assert response.status_code == 200
    assert response.data["user"]["username"] == playlist.user.username
