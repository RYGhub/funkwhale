import datetime

from funkwhale_api.federation import utils as federation_utils
from funkwhale_api.music import models


def test_can_create_artist_from_api(artists, mocker, db):
    mocker.patch(
        "musicbrainzngs.search_artists",
        return_value=artists["search"]["adhesive_wombat"],
    )
    artist = models.Artist.create_from_api(query="Adhesive wombat")
    data = models.Artist.api.search(query="Adhesive wombat")["artist-list"][0]

    assert int(data["ext:score"]), 100
    assert data["id"], "62c3befb-6366-4585-b256-809472333801"
    assert artist.mbid, data["id"]
    assert artist.name, "Adhesive Wombat"
    assert artist.fid == federation_utils.full_url(
        "/federation/music/artists/{}".format(artist.uuid)
    )


def test_can_create_album_from_api(artists, albums, mocker, db):
    mocker.patch(
        "funkwhale_api.musicbrainz.api.releases.search",
        return_value=albums["search"]["hypnotize"],
    )
    mocker.patch(
        "funkwhale_api.musicbrainz.api.artists.get", return_value=artists["get"]["soad"]
    )
    album = models.Album.create_from_api(
        query="Hypnotize", artist="system of a down", type="album"
    )
    data = models.Album.api.search(
        query="Hypnotize", artist="system of a down", type="album"
    )["release-list"][0]

    assert album.mbid, data["id"]
    assert album.title, "Hypnotize"
    assert album.release_date, datetime.date(2005, 1, 1)
    assert album.artist.name, "System of a Down"
    assert album.artist.mbid, data["artist-credit"][0]["artist"]["id"]
    assert album.fid == federation_utils.full_url(
        "/federation/music/albums/{}".format(album.uuid)
    )


def test_can_create_track_from_api(artists, albums, tracks, mocker, db):
    mocker.patch(
        "funkwhale_api.musicbrainz.api.artists.get",
        return_value=artists["get"]["adhesive_wombat"],
    )
    mocker.patch(
        "funkwhale_api.musicbrainz.api.releases.get",
        return_value=albums["get"]["marsupial"],
    )
    mocker.patch(
        "funkwhale_api.musicbrainz.api.recordings.search",
        return_value=tracks["search"]["8bitadventures"],
    )
    track = models.Track.create_from_api(query="8-bit adventure")
    data = models.Track.api.search(query="8-bit adventure")["recording-list"][0]
    assert int(data["ext:score"]) == 100
    assert data["id"] == "9968a9d6-8d92-4051-8f76-674e157b6eed"
    assert track.mbid == data["id"]
    assert track.artist.pk is not None
    assert str(track.artist.mbid) == "62c3befb-6366-4585-b256-809472333801"
    assert track.artist.name == "Adhesive Wombat"
    assert str(track.album.mbid) == "a50d2a81-2a50-484d-9cb4-b9f6833f583e"
    assert track.album.title == "Marsupial Madness"
    assert track.fid == federation_utils.full_url(
        "/federation/music/tracks/{}".format(track.uuid)
    )


def test_can_create_track_from_api_with_corresponding_tags(
    artists, albums, tracks, mocker, db
):
    mocker.patch(
        "funkwhale_api.musicbrainz.api.artists.get",
        return_value=artists["get"]["adhesive_wombat"],
    )
    mocker.patch(
        "funkwhale_api.musicbrainz.api.releases.get",
        return_value=albums["get"]["marsupial"],
    )
    mocker.patch(
        "funkwhale_api.musicbrainz.api.recordings.get",
        return_value=tracks["get"]["8bitadventures"],
    )
    track = models.Track.create_from_api(id="9968a9d6-8d92-4051-8f76-674e157b6eed")
    expected_tags = ["techno", "good-music"]
    track_tags = track.tagged_items.values_list("tag__name", flat=True)
    for tag in expected_tags:
        assert tag in track_tags


def test_can_get_or_create_track_from_api(artists, albums, tracks, mocker, db):
    mocker.patch(
        "funkwhale_api.musicbrainz.api.artists.get",
        return_value=artists["get"]["adhesive_wombat"],
    )
    mocker.patch(
        "funkwhale_api.musicbrainz.api.releases.get",
        return_value=albums["get"]["marsupial"],
    )
    mocker.patch(
        "funkwhale_api.musicbrainz.api.recordings.search",
        return_value=tracks["search"]["8bitadventures"],
    )
    track = models.Track.create_from_api(query="8-bit adventure")
    data = models.Track.api.search(query="8-bit adventure")["recording-list"][0]
    assert int(data["ext:score"]) == 100
    assert data["id"] == "9968a9d6-8d92-4051-8f76-674e157b6eed"
    assert track.mbid == data["id"]
    assert track.artist.pk is not None
    assert str(track.artist.mbid) == "62c3befb-6366-4585-b256-809472333801"
    assert track.artist.name == "Adhesive Wombat"

    track2, created = models.Track.get_or_create_from_api(mbid=data["id"])
    assert not created
    assert track == track2
