import datetime
import json

import pytest
from django.urls import reverse
from django.utils import timezone

import funkwhale_api

from funkwhale_api.music import models as music_models
from funkwhale_api.music import views as music_views
from funkwhale_api.subsonic import renderers, serializers


def render_json(data):
    return json.loads(renderers.SubsonicJSONRenderer().render(data))


def test_render_content_json(db, api_client):
    url = reverse("api:subsonic-ping")
    response = api_client.get(url, {"f": "json"})

    expected = {
        "status": "ok",
        "version": "1.16.0",
        "type": "funkwhale",
        "funkwhale-version": funkwhale_api.__version__,
    }
    assert response.status_code == 200
    assert json.loads(response.content) == render_json(expected)


@pytest.mark.parametrize("f", ["xml", "json"])
def test_exception_wrong_credentials(f, db, api_client):
    url = reverse("api:subsonic-ping")
    response = api_client.get(url, {"f": f, "u": "yolo"})

    expected = {
        "status": "failed",
        "error": {"code": 40, "message": "Wrong username or password."},
    }
    assert response.status_code == 200
    assert response.data == expected


def test_disabled_subsonic(preferences, api_client):
    preferences["subsonic__enabled"] = False
    url = reverse("api:subsonic-ping")
    response = api_client.get(url)
    assert response.status_code == 405


@pytest.mark.parametrize("f", ["xml", "json"])
def test_get_license(f, db, logged_in_api_client, mocker):
    url = reverse("api:subsonic-get-license")
    assert url.endswith("getLicense") is True
    now = timezone.now()
    mocker.patch("django.utils.timezone.now", return_value=now)
    response = logged_in_api_client.get(url, {"f": f})
    expected = {
        "status": "ok",
        "version": "1.16.0",
        "license": {
            "valid": "true",
            "email": "valid@valid.license",
            "licenseExpires": now + datetime.timedelta(days=365),
        },
    }
    assert response.status_code == 200
    assert response.data == expected


@pytest.mark.parametrize("f", ["xml", "json"])
def test_ping(f, db, api_client):
    url = reverse("api:subsonic-ping")
    response = api_client.get(url, {"f": f})

    expected = {"status": "ok", "version": "1.16.0"}
    assert response.status_code == 200
    assert response.data == expected


@pytest.mark.parametrize("f", ["xml", "json"])
def test_get_artists(
    f, db, logged_in_api_client, factories, mocker, queryset_equal_queries
):
    url = reverse("api:subsonic-get-artists")
    assert url.endswith("getArtists") is True
    factories["music.Artist"].create_batch(size=3, playable=True)
    playable_by = mocker.spy(music_models.ArtistQuerySet, "playable_by")
    expected = {
        "artists": serializers.GetArtistsSerializer(
            music_models.Artist.objects.all()
        ).data
    }
    response = logged_in_api_client.get(url, {"f": f})

    assert response.status_code == 200
    assert response.data == expected
    playable_by.assert_called_once_with(music_models.Artist.objects.all(), None)


@pytest.mark.parametrize("f", ["xml", "json"])
def test_get_artist(
    f, db, logged_in_api_client, factories, mocker, queryset_equal_queries
):
    url = reverse("api:subsonic-get-artist")
    assert url.endswith("getArtist") is True
    artist = factories["music.Artist"](playable=True)
    factories["music.Album"].create_batch(size=3, artist=artist, playable=True)
    playable_by = mocker.spy(music_models.ArtistQuerySet, "playable_by")

    expected = {"artist": serializers.GetArtistSerializer(artist).data}
    response = logged_in_api_client.get(url, {"id": artist.pk})

    assert response.status_code == 200
    assert response.data == expected
    playable_by.assert_called_once_with(music_models.Artist.objects.all(), None)


@pytest.mark.parametrize("f", ["xml", "json"])
def test_get_invalid_artist(f, db, logged_in_api_client, factories):
    url = reverse("api:subsonic-get-artist")
    assert url.endswith("getArtist") is True
    expected = {"error": {"code": 0, "message": 'For input string "asdf"'}}
    response = logged_in_api_client.get(url, {"id": "asdf"})

    assert response.status_code == 200
    assert response.data == expected


@pytest.mark.parametrize("f", ["xml", "json"])
def test_get_artist_info2(
    f, db, logged_in_api_client, factories, mocker, queryset_equal_queries
):
    url = reverse("api:subsonic-get-artist-info2")
    assert url.endswith("getArtistInfo2") is True
    artist = factories["music.Artist"](playable=True)
    playable_by = mocker.spy(music_models.ArtistQuerySet, "playable_by")

    expected = {"artist-info2": {}}
    response = logged_in_api_client.get(url, {"id": artist.pk})

    assert response.status_code == 200
    assert response.data == expected

    playable_by.assert_called_once_with(music_models.Artist.objects.all(), None)


@pytest.mark.parametrize("f", ["xml", "json"])
def test_get_album(
    f, db, logged_in_api_client, factories, mocker, queryset_equal_queries
):
    url = reverse("api:subsonic-get-album")
    assert url.endswith("getAlbum") is True
    artist = factories["music.Artist"]()
    album = factories["music.Album"](artist=artist)
    factories["music.Track"].create_batch(size=3, album=album, playable=True)
    playable_by = mocker.spy(music_models.AlbumQuerySet, "playable_by")
    expected = {"album": serializers.GetAlbumSerializer(album).data}
    response = logged_in_api_client.get(url, {"f": f, "id": album.pk})

    assert response.status_code == 200
    assert response.data == expected

    playable_by.assert_called_once_with(
        music_models.Album.objects.select_related("artist"), None
    )


@pytest.mark.parametrize("f", ["xml", "json"])
def test_get_song(
    f, db, logged_in_api_client, factories, mocker, queryset_equal_queries
):
    url = reverse("api:subsonic-get-song")
    assert url.endswith("getSong") is True
    artist = factories["music.Artist"]()
    album = factories["music.Album"](artist=artist)
    track = factories["music.Track"](album=album, playable=True)
    upload = factories["music.Upload"](track=track)
    playable_by = mocker.spy(music_models.TrackQuerySet, "playable_by")
    response = logged_in_api_client.get(url, {"f": f, "id": track.pk})

    assert response.status_code == 200
    assert response.data == {
        "song": serializers.get_track_data(track.album, track, upload)
    }
    playable_by.assert_called_once_with(music_models.Track.objects.all(), None)


@pytest.mark.parametrize("f", ["xml", "json"])
def test_stream(f, db, logged_in_api_client, factories, mocker, queryset_equal_queries):
    url = reverse("api:subsonic-stream")
    mocked_serve = mocker.spy(music_views, "handle_serve")
    assert url.endswith("stream") is True
    upload = factories["music.Upload"](playable=True)
    playable_by = mocker.spy(music_models.TrackQuerySet, "playable_by")
    response = logged_in_api_client.get(url, {"f": f, "id": upload.track.pk})

    mocked_serve.assert_called_once_with(upload=upload, user=logged_in_api_client.user)
    assert response.status_code == 200
    playable_by.assert_called_once_with(music_models.Track.objects.all(), None)


@pytest.mark.parametrize("f", ["xml", "json"])
def test_star(f, db, logged_in_api_client, factories):
    url = reverse("api:subsonic-star")
    assert url.endswith("star") is True
    track = factories["music.Track"]()
    response = logged_in_api_client.get(url, {"f": f, "id": track.pk})

    assert response.status_code == 200
    assert response.data == {"status": "ok"}

    favorite = logged_in_api_client.user.track_favorites.latest("id")
    assert favorite.track == track


@pytest.mark.parametrize("f", ["xml", "json"])
def test_unstar(f, db, logged_in_api_client, factories):
    url = reverse("api:subsonic-unstar")
    assert url.endswith("unstar") is True
    track = factories["music.Track"]()
    factories["favorites.TrackFavorite"](track=track, user=logged_in_api_client.user)
    response = logged_in_api_client.get(url, {"f": f, "id": track.pk})

    assert response.status_code == 200
    assert response.data == {"status": "ok"}
    assert logged_in_api_client.user.track_favorites.count() == 0


@pytest.mark.parametrize("f", ["xml", "json"])
def test_get_starred2(f, db, logged_in_api_client, factories):
    url = reverse("api:subsonic-get-starred2")
    assert url.endswith("getStarred2") is True
    track = factories["music.Track"]()
    favorite = factories["favorites.TrackFavorite"](
        track=track, user=logged_in_api_client.user
    )
    response = logged_in_api_client.get(url, {"f": f, "id": track.pk})

    assert response.status_code == 200
    assert response.data == {
        "starred2": {"song": serializers.get_starred_tracks_data([favorite])}
    }


@pytest.mark.parametrize("f", ["xml", "json"])
def test_get_starred(f, db, logged_in_api_client, factories):
    url = reverse("api:subsonic-get-starred")
    assert url.endswith("getStarred") is True
    track = factories["music.Track"]()
    favorite = factories["favorites.TrackFavorite"](
        track=track, user=logged_in_api_client.user
    )
    response = logged_in_api_client.get(url, {"f": f, "id": track.pk})

    assert response.status_code == 200
    assert response.data == {
        "starred": {"song": serializers.get_starred_tracks_data([favorite])}
    }


@pytest.mark.parametrize("f", ["xml", "json"])
def test_get_album_list2(
    f, db, logged_in_api_client, factories, mocker, queryset_equal_queries
):
    url = reverse("api:subsonic-get-album-list2")
    assert url.endswith("getAlbumList2") is True
    album1 = factories["music.Album"](playable=True)
    album2 = factories["music.Album"](playable=True)
    factories["music.Album"]()
    playable_by = mocker.spy(music_models.AlbumQuerySet, "playable_by")
    response = logged_in_api_client.get(url, {"f": f, "type": "newest"})

    assert response.status_code == 200
    assert response.data == {
        "albumList2": {"album": serializers.get_album_list2_data([album2, album1])}
    }
    playable_by.assert_called_once()


@pytest.mark.parametrize("f", ["xml", "json"])
def test_get_album_list2_pagination(f, db, logged_in_api_client, factories):
    url = reverse("api:subsonic-get-album-list2")
    assert url.endswith("getAlbumList2") is True
    album1 = factories["music.Album"](playable=True)
    factories["music.Album"](playable=True)
    response = logged_in_api_client.get(
        url, {"f": f, "type": "newest", "size": 1, "offset": 1}
    )

    assert response.status_code == 200
    assert response.data == {
        "albumList2": {"album": serializers.get_album_list2_data([album1])}
    }


@pytest.mark.parametrize("f", ["xml", "json"])
def test_search3(f, db, logged_in_api_client, factories):
    url = reverse("api:subsonic-search3")
    assert url.endswith("search3") is True
    artist = factories["music.Artist"](name="testvalue", playable=True)
    factories["music.Artist"](name="nope")
    factories["music.Artist"](name="nope2", playable=True)
    album = factories["music.Album"](title="testvalue", playable=True)
    factories["music.Album"](title="nope")
    factories["music.Album"](title="nope2", playable=True)
    track = factories["music.Track"](title="testvalue", playable=True)
    factories["music.Track"](title="nope")
    factories["music.Track"](title="nope2", playable=True)

    response = logged_in_api_client.get(url, {"f": f, "query": "testval"})

    artist_qs = (
        music_models.Artist.objects.with_albums_count()
        .filter(pk=artist.pk)
        .values("_albums_count", "id", "name")
    )
    assert response.status_code == 200
    assert response.data == {
        "searchResult3": {
            "artist": [serializers.get_artist_data(a) for a in artist_qs],
            "album": serializers.get_album_list2_data([album]),
            "song": serializers.get_song_list_data([track]),
        }
    }


@pytest.mark.parametrize("f", ["xml", "json"])
def test_get_playlists(f, db, logged_in_api_client, factories):
    url = reverse("api:subsonic-get-playlists")
    assert url.endswith("getPlaylists") is True
    playlist = factories["playlists.Playlist"](user=logged_in_api_client.user)
    response = logged_in_api_client.get(url, {"f": f})

    qs = playlist.__class__.objects.with_tracks_count()
    assert response.status_code == 200
    assert response.data == {
        "playlists": {"playlist": [serializers.get_playlist_data(qs.first())]}
    }


@pytest.mark.parametrize("f", ["xml", "json"])
def test_get_playlist(f, db, logged_in_api_client, factories):
    url = reverse("api:subsonic-get-playlist")
    assert url.endswith("getPlaylist") is True
    playlist = factories["playlists.Playlist"](user=logged_in_api_client.user)
    response = logged_in_api_client.get(url, {"f": f, "id": playlist.pk})

    qs = playlist.__class__.objects.with_tracks_count()
    assert response.status_code == 200
    assert response.data == {
        "playlist": serializers.get_playlist_detail_data(qs.first())
    }


@pytest.mark.parametrize("f", ["xml", "json"])
def test_update_playlist(f, db, logged_in_api_client, factories):
    url = reverse("api:subsonic-update-playlist")
    assert url.endswith("updatePlaylist") is True
    playlist = factories["playlists.Playlist"](user=logged_in_api_client.user)
    factories["playlists.PlaylistTrack"](index=0, playlist=playlist)
    new_track = factories["music.Track"]()
    response = logged_in_api_client.get(
        url,
        {
            "f": f,
            "name": "new_name",
            "playlistId": playlist.pk,
            "songIdToAdd": new_track.pk,
            "songIndexToRemove": 0,
        },
    )
    playlist.refresh_from_db()
    assert response.status_code == 200
    assert playlist.name == "new_name"
    assert playlist.playlist_tracks.count() == 1
    assert playlist.playlist_tracks.first().track_id == new_track.pk


@pytest.mark.parametrize("f", ["xml", "json"])
def test_delete_playlist(f, db, logged_in_api_client, factories):
    url = reverse("api:subsonic-delete-playlist")
    assert url.endswith("deletePlaylist") is True
    playlist = factories["playlists.Playlist"](user=logged_in_api_client.user)
    response = logged_in_api_client.get(url, {"f": f, "id": playlist.pk})
    assert response.status_code == 200
    with pytest.raises(playlist.__class__.DoesNotExist):
        playlist.refresh_from_db()


@pytest.mark.parametrize("f", ["xml", "json"])
def test_create_playlist(f, db, logged_in_api_client, factories):
    url = reverse("api:subsonic-create-playlist")
    assert url.endswith("createPlaylist") is True
    track1 = factories["music.Track"]()
    track2 = factories["music.Track"]()
    response = logged_in_api_client.get(
        url, {"f": f, "name": "hello", "songId": [track1.pk, track2.pk]}
    )
    assert response.status_code == 200
    playlist = logged_in_api_client.user.playlists.latest("id")
    assert playlist.playlist_tracks.count() == 2
    for i, t in enumerate([track1, track2]):
        plt = playlist.playlist_tracks.get(track=t)
        assert plt.index == i
    assert playlist.name == "hello"
    qs = playlist.__class__.objects.with_tracks_count()
    assert response.data == {
        "playlist": serializers.get_playlist_detail_data(qs.first())
    }


@pytest.mark.parametrize("f", ["xml", "json"])
def test_get_music_folders(f, db, logged_in_api_client, factories):
    url = reverse("api:subsonic-get-music-folders")
    assert url.endswith("getMusicFolders") is True
    response = logged_in_api_client.get(url, {"f": f})
    assert response.status_code == 200
    assert response.data == {
        "musicFolders": {"musicFolder": [{"id": 1, "name": "Music"}]}
    }


@pytest.mark.parametrize("f", ["xml", "json"])
def test_get_indexes(
    f, db, logged_in_api_client, factories, mocker, queryset_equal_queries
):
    url = reverse("api:subsonic-get-indexes")
    assert url.endswith("getIndexes") is True
    factories["music.Artist"].create_batch(size=3, playable=True)
    expected = {
        "indexes": serializers.GetArtistsSerializer(
            music_models.Artist.objects.all()
        ).data
    }
    playable_by = mocker.spy(music_models.ArtistQuerySet, "playable_by")
    response = logged_in_api_client.get(url)

    assert response.status_code == 200
    assert response.data == expected

    playable_by.assert_called_once_with(music_models.Artist.objects.all(), None)


def test_get_cover_art_album(factories, logged_in_api_client):
    url = reverse("api:subsonic-get-cover-art")
    assert url.endswith("getCoverArt") is True
    album = factories["music.Album"]()
    response = logged_in_api_client.get(url, {"id": "al-{}".format(album.pk)})

    assert response.status_code == 200
    assert response["Content-Type"] == ""
    assert response["X-Accel-Redirect"] == music_views.get_file_path(
        album.cover
    ).decode("utf-8")


def test_scrobble(factories, logged_in_api_client):
    upload = factories["music.Upload"]()
    track = upload.track
    url = reverse("api:subsonic-scrobble")
    assert url.endswith("scrobble") is True
    response = logged_in_api_client.get(url, {"id": track.pk, "submission": True})

    assert response.status_code == 200

    listening = logged_in_api_client.user.listenings.latest("id")
    assert listening.track == track
