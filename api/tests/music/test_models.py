import os

import pytest

from django.utils import timezone

from funkwhale_api.music import importers, models, tasks

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def test_can_store_release_group_id_on_album(factories):
    album = factories["music.Album"]()
    assert album.release_group_id is not None


def test_import_album_stores_release_group(factories):
    album_data = {
        "artist-credit": [
            {
                "artist": {
                    "disambiguation": "George Shaw",
                    "id": "62c3befb-6366-4585-b256-809472333801",
                    "name": "Adhesive Wombat",
                    "sort-name": "Wombat, Adhesive",
                }
            }
        ],
        "artist-credit-phrase": "Adhesive Wombat",
        "country": "XW",
        "date": "2013-06-05",
        "id": "a50d2a81-2a50-484d-9cb4-b9f6833f583e",
        "status": "Official",
        "title": "Marsupial Madness",
        "release-group": {"id": "447b4979-2178-405c-bfe6-46bf0b09e6c7"},
    }
    artist = factories["music.Artist"](
        mbid=album_data["artist-credit"][0]["artist"]["id"]
    )
    cleaned_data = models.Album.clean_musicbrainz_data(album_data)
    album = importers.load(models.Album, cleaned_data, album_data, import_hooks=[])

    assert album.release_group_id == album_data["release-group"]["id"]
    assert album.artist == artist


def test_import_track_from_release(factories, mocker):
    album = factories["music.Album"](mbid="430347cb-0879-3113-9fde-c75b658c298e")
    artist = factories["music.Artist"](mbid="a5211c65-2465-406b-93ec-213588869dc1")
    album_data = {
        "release": {
            "id": album.mbid,
            "title": "Daydream Nation",
            "status": "Official",
            "medium-count": 1,
            "medium-list": [
                {
                    "position": "1",
                    "format": "CD",
                    "track-list": [
                        {
                            "id": "03baca8b-855a-3c05-8f3d-d3235287d84d",
                            "position": "4",
                            "number": "4",
                            "length": "417973",
                            "recording": {
                                "id": "2109e376-132b-40ad-b993-2bb6812e19d4",
                                "title": "Teen Age Riot",
                                "length": "417973",
                                "artist-credit": [
                                    {"artist": {"id": artist.mbid, "name": artist.name}}
                                ],
                            },
                            "track_or_recording_length": "417973",
                        }
                    ],
                    "track-count": 1,
                }
            ],
        }
    }
    mocked_get = mocker.patch(
        "funkwhale_api.musicbrainz.api.releases.get", return_value=album_data
    )
    track_data = album_data["release"]["medium-list"][0]["track-list"][0]
    track = models.Track.get_or_create_from_release(
        "430347cb-0879-3113-9fde-c75b658c298e", track_data["recording"]["id"]
    )[0]
    mocked_get.assert_called_once_with(album.mbid, includes=models.Album.api_includes)
    assert track.title == track_data["recording"]["title"]
    assert track.mbid == track_data["recording"]["id"]
    assert track.album == album
    assert track.artist == artist
    assert track.position == int(track_data["position"])


def test_import_track_with_different_artist_than_release(factories, mocker):
    album = factories["music.Album"](mbid="430347cb-0879-3113-9fde-c75b658c298e")
    recording_data = {
        "recording": {
            "id": "94ab07eb-bdf3-4155-b471-ba1dc85108bf",
            "title": "Flaming Red Hair",
            "length": "159000",
            "artist-credit": [
                {
                    "artist": {
                        "id": "a5211c65-2465-406b-93ec-213588869dc1",
                        "name": "Plan 9",
                        "sort-name": "Plan 9",
                        "disambiguation": "New Zealand group",
                    }
                }
            ],
            "release-list": [
                {
                    "id": album.mbid,
                    "title": "The Lord of the Rings: The Fellowship of the Ring - The Complete Recordings",
                    "status": "Official",
                    "quality": "normal",
                    "text-representation": {"language": "eng", "script": "Latn"},
                    "artist-credit": [
                        {
                            "artist": {
                                "id": "9b58672a-e68e-4972-956e-a8985a165a1f",
                                "name": "Howard Shore",
                                "sort-name": "Shore, Howard",
                            }
                        }
                    ],
                    "date": "2005-12-13",
                    "country": "US",
                    "release-event-count": 1,
                    "barcode": "093624945420",
                    "artist-credit-phrase": "Howard Shore",
                }
            ],
            "release-count": 3,
            "artist-credit-phrase": "Plan 9",
        }
    }
    artist = factories["music.Artist"](mbid="a5211c65-2465-406b-93ec-213588869dc1")
    mocker.patch(
        "funkwhale_api.musicbrainz.api.recordings.get", return_value=recording_data
    )

    track = models.Track.get_or_create_from_api(recording_data["recording"]["id"])[0]
    assert track.title == recording_data["recording"]["title"]
    assert track.mbid == recording_data["recording"]["id"]
    assert track.album == album
    assert track.artist == artist


@pytest.mark.parametrize(
    "extention,mimetype", [("ogg", "audio/ogg"), ("mp3", "audio/mpeg")]
)
def test_audio_track_mime_type(extention, mimetype, factories):

    name = ".".join(["test", extention])
    path = os.path.join(DATA_DIR, name)
    tf = factories["music.TrackFile"](audio_file__from_path=path, mimetype=None)

    assert tf.mimetype == mimetype


def test_track_file_file_name(factories):
    name = "test.mp3"
    path = os.path.join(DATA_DIR, name)
    tf = factories["music.TrackFile"](audio_file__from_path=path)

    assert tf.filename == tf.track.full_name + ".mp3"


def test_track_get_file_size(factories):
    name = "test.mp3"
    path = os.path.join(DATA_DIR, name)
    tf = factories["music.TrackFile"](audio_file__from_path=path)

    assert tf.get_file_size() == 297745


def test_track_get_file_size_in_place(factories):
    name = "test.mp3"
    path = os.path.join(DATA_DIR, name)
    tf = factories["music.TrackFile"](in_place=True, source="file://{}".format(path))

    assert tf.get_file_size() == 297745


def test_album_get_image_content(factories):
    album = factories["music.Album"]()
    album.get_image(data={"content": b"test", "mimetype": "image/jpeg"})
    album.refresh_from_db()

    assert album.cover.read() == b"test"


def test_library(factories):
    now = timezone.now()
    actor = factories["federation.Actor"]()
    library = factories["music.Library"](
        name="Hello world", description="hello", actor=actor, privacy_level="instance"
    )

    assert library.creation_date >= now
    assert library.files.count() == 0
    assert library.uuid is not None


@pytest.mark.parametrize(
    "privacy_level,expected", [("me", True), ("instance", True), ("everyone", True)]
)
def test_playable_by_correct_actor(privacy_level, expected, factories):
    tf = factories["music.TrackFile"](library__privacy_level=privacy_level)
    queryset = tf.library.files.playable_by(tf.library.actor)
    match = tf in list(queryset)
    assert match is expected


@pytest.mark.parametrize(
    "privacy_level,expected", [("me", False), ("instance", True), ("everyone", True)]
)
def test_playable_by_instance_actor(privacy_level, expected, factories):
    tf = factories["music.TrackFile"](library__privacy_level=privacy_level)
    instance_actor = factories["federation.Actor"](domain=tf.library.actor.domain)
    queryset = tf.library.files.playable_by(instance_actor)
    match = tf in list(queryset)
    assert match is expected


@pytest.mark.parametrize(
    "privacy_level,expected", [("me", False), ("instance", False), ("everyone", True)]
)
def test_playable_by_anonymous(privacy_level, expected, factories):
    tf = factories["music.TrackFile"](library__privacy_level=privacy_level)
    queryset = tf.library.files.playable_by(None)
    match = tf in list(queryset)
    assert match is expected


@pytest.mark.parametrize(
    "privacy_level,expected", [("me", True), ("instance", True), ("everyone", True)]
)
def test_track_playable_by_correct_actor(privacy_level, expected, factories):
    tf = factories["music.TrackFile"]()
    queryset = models.Track.objects.playable_by(
        tf.library.actor
    ).annotate_playable_by_actor(tf.library.actor)
    match = tf.track in list(queryset)
    assert match is expected
    if expected:
        assert bool(queryset.first().is_playable_by_actor) is expected


@pytest.mark.parametrize(
    "privacy_level,expected", [("me", False), ("instance", True), ("everyone", True)]
)
def test_track_playable_by_instance_actor(privacy_level, expected, factories):
    tf = factories["music.TrackFile"](library__privacy_level=privacy_level)
    instance_actor = factories["federation.Actor"](domain=tf.library.actor.domain)
    queryset = models.Track.objects.playable_by(
        instance_actor
    ).annotate_playable_by_actor(instance_actor)
    match = tf.track in list(queryset)
    assert match is expected
    if expected:
        assert bool(queryset.first().is_playable_by_actor) is expected


@pytest.mark.parametrize(
    "privacy_level,expected", [("me", False), ("instance", False), ("everyone", True)]
)
def test_track_playable_by_anonymous(privacy_level, expected, factories):
    tf = factories["music.TrackFile"](library__privacy_level=privacy_level)
    queryset = models.Track.objects.playable_by(None).annotate_playable_by_actor(None)
    match = tf.track in list(queryset)
    assert match is expected
    if expected:
        assert bool(queryset.first().is_playable_by_actor) is expected


@pytest.mark.parametrize(
    "privacy_level,expected", [("me", True), ("instance", True), ("everyone", True)]
)
def test_album_playable_by_correct_actor(privacy_level, expected, factories):
    tf = factories["music.TrackFile"]()

    queryset = models.Album.objects.playable_by(
        tf.library.actor
    ).annotate_playable_by_actor(tf.library.actor)
    match = tf.track.album in list(queryset)
    assert match is expected
    if expected:
        assert bool(queryset.first().is_playable_by_actor) is expected


@pytest.mark.parametrize(
    "privacy_level,expected", [("me", False), ("instance", True), ("everyone", True)]
)
def test_album_playable_by_instance_actor(privacy_level, expected, factories):
    tf = factories["music.TrackFile"](library__privacy_level=privacy_level)
    instance_actor = factories["federation.Actor"](domain=tf.library.actor.domain)
    queryset = models.Album.objects.playable_by(
        instance_actor
    ).annotate_playable_by_actor(instance_actor)
    match = tf.track.album in list(queryset)
    assert match is expected
    if expected:
        assert bool(queryset.first().is_playable_by_actor) is expected


@pytest.mark.parametrize(
    "privacy_level,expected", [("me", False), ("instance", False), ("everyone", True)]
)
def test_album_playable_by_anonymous(privacy_level, expected, factories):
    tf = factories["music.TrackFile"](library__privacy_level=privacy_level)
    queryset = models.Album.objects.playable_by(None).annotate_playable_by_actor(None)
    match = tf.track.album in list(queryset)
    assert match is expected
    if expected:
        assert bool(queryset.first().is_playable_by_actor) is expected


@pytest.mark.parametrize(
    "privacy_level,expected", [("me", True), ("instance", True), ("everyone", True)]
)
def test_artist_playable_by_correct_actor(privacy_level, expected, factories):
    tf = factories["music.TrackFile"]()

    queryset = models.Artist.objects.playable_by(
        tf.library.actor
    ).annotate_playable_by_actor(tf.library.actor)
    match = tf.track.artist in list(queryset)
    assert match is expected
    if expected:
        assert bool(queryset.first().is_playable_by_actor) is expected


@pytest.mark.parametrize(
    "privacy_level,expected", [("me", False), ("instance", True), ("everyone", True)]
)
def test_artist_playable_by_instance_actor(privacy_level, expected, factories):
    tf = factories["music.TrackFile"](library__privacy_level=privacy_level)
    instance_actor = factories["federation.Actor"](domain=tf.library.actor.domain)
    queryset = models.Artist.objects.playable_by(
        instance_actor
    ).annotate_playable_by_actor(instance_actor)
    match = tf.track.artist in list(queryset)
    assert match is expected
    if expected:
        assert bool(queryset.first().is_playable_by_actor) is expected


@pytest.mark.parametrize(
    "privacy_level,expected", [("me", False), ("instance", False), ("everyone", True)]
)
def test_artist_playable_by_anonymous(privacy_level, expected, factories):
    tf = factories["music.TrackFile"](library__privacy_level=privacy_level)
    queryset = models.Artist.objects.playable_by(None).annotate_playable_by_actor(None)
    match = tf.track.artist in list(queryset)
    assert match is expected
    if expected:
        assert bool(queryset.first().is_playable_by_actor) is expected


def test_track_file_listen_url(factories):
    tf = factories["music.TrackFile"]()
    expected = tf.track.listen_url + "?file={}".format(tf.uuid)

    assert tf.listen_url == expected


def test_library_schedule_scan(factories, now, mocker):
    on_commit = mocker.patch("funkwhale_api.common.utils.on_commit")
    library = factories["music.Library"](files_count=5)

    scan = library.schedule_scan()

    assert scan.creation_date >= now
    assert scan.status == "pending"
    assert scan.library == library
    assert scan.total_files == 5
    assert scan.processed_files == 0
    assert scan.errored_files == 0
    assert scan.modification_date is None

    on_commit.assert_called_once_with(
        tasks.start_library_scan.delay, library_scan_id=scan.pk
    )


def test_library_schedule_scan_too_recent(factories, now):
    scan = factories["music.LibraryScan"]()
    result = scan.library.schedule_scan()

    assert result is None
    assert scan.library.scans.count() == 1


def test_get_audio_data(factories):
    tf = factories["music.TrackFile"]()

    result = tf.get_audio_data()

    assert result == {"duration": 229, "bitrate": 128000, "size": 3459481}


@pytest.mark.skip(reason="Refactoring in progress")
def test_library_viewable_by():
    assert False


def test_library_queryset_with_follows(factories):
    library1 = factories["music.Library"]()
    library2 = factories["music.Library"]()
    follow = factories["federation.LibraryFollow"](target=library2)
    qs = library1.__class__.objects.with_follows(follow.actor).order_by("pk")

    l1 = list(qs)[0]
    l2 = list(qs)[1]
    assert l1._follows == []
    assert l2._follows == [follow]
