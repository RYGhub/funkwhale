import datetime
import io
import os
import pytest
import uuid

from django.core.paginator import Paginator
from django.utils import timezone

from funkwhale_api.federation import serializers as federation_serializers
from funkwhale_api.federation import jsonld
from funkwhale_api.music import licenses, metadata, signals, tasks

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


# DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")


def test_can_create_track_from_file_metadata_no_mbid(db, mocker):
    metadata = {
        "title": "Test track",
        "artist": "Test artist",
        "album": "Test album",
        "date": datetime.date(2012, 8, 15),
        "track_number": 4,
        "disc_number": 2,
        "license": "Hello world: http://creativecommons.org/licenses/by-sa/4.0/",
        "copyright": "2018 Someone",
    }
    mocker.patch("funkwhale_api.music.metadata.Metadata.all", return_value=metadata)
    match_license = mocker.spy(licenses, "match")

    track = tasks.get_track_from_import_metadata(metadata)

    assert track.title == metadata["title"]
    assert track.mbid is None
    assert track.position == 4
    assert track.disc_number == 2
    assert track.license.code == "cc-by-sa-4.0"
    assert track.copyright == metadata["copyright"]
    assert track.album.title == metadata["album"]
    assert track.album.mbid is None
    assert track.album.release_date == datetime.date(2012, 8, 15)
    assert track.artist.name == metadata["artist"]
    assert track.artist.mbid is None
    match_license.assert_called_once_with(metadata["license"], metadata["copyright"])


def test_can_create_track_from_file_metadata_mbid(factories, mocker):
    metadata = {
        "title": "Test track",
        "artist": "Test artist",
        "album_artist": "Test album artist",
        "album": "Test album",
        "date": datetime.date(2012, 8, 15),
        "track_number": 4,
        "musicbrainz_albumid": "ce40cdb1-a562-4fd8-a269-9269f98d4124",
        "musicbrainz_recordingid": "f269d497-1cc0-4ae4-a0c4-157ec7d73fcb",
        "musicbrainz_artistid": "9c6bddde-6228-4d9f-ad0d-03f6fcb19e13",
        "musicbrainz_albumartistid": "9c6bddde-6478-4d9f-ad0d-03f6fcb19e13",
        "cover_data": {"content": b"image_content", "mimetype": "image/png"},
    }

    mocker.patch("funkwhale_api.music.metadata.Metadata.all", return_value=metadata)

    track = tasks.get_track_from_import_metadata(metadata)

    assert track.title == metadata["title"]
    assert track.mbid == metadata["musicbrainz_recordingid"]
    assert track.position == 4
    assert track.disc_number is None
    assert track.album.title == metadata["album"]
    assert track.album.mbid == metadata["musicbrainz_albumid"]
    assert track.album.artist.mbid == metadata["musicbrainz_albumartistid"]
    assert track.album.artist.name == metadata["album_artist"]
    assert track.album.release_date == datetime.date(2012, 8, 15)
    assert track.artist.name == metadata["artist"]
    assert track.artist.mbid == metadata["musicbrainz_artistid"]


def test_can_create_track_from_file_metadata_mbid_existing_album_artist(
    factories, mocker
):
    artist = factories["music.Artist"]()
    album = factories["music.Album"]()
    metadata = {
        "artist": "",
        "album": "",
        "title": "Hello",
        "track_number": 4,
        "musicbrainz_albumid": album.mbid,
        "musicbrainz_recordingid": "f269d497-1cc0-4ae4-a0c4-157ec7d73fcb",
        "musicbrainz_artistid": artist.mbid,
        "musicbrainz_albumartistid": album.artist.mbid,
    }

    mocker.patch("funkwhale_api.music.metadata.Metadata.all", return_value=metadata)

    track = tasks.get_track_from_import_metadata(metadata)

    assert track.title == metadata["title"]
    assert track.mbid == metadata["musicbrainz_recordingid"]
    assert track.position == 4
    assert track.album == album
    assert track.artist == artist


def test_can_create_track_from_file_metadata_fid_existing_album_artist(
    factories, mocker
):
    artist = factories["music.Artist"]()
    album = factories["music.Album"]()
    metadata = {
        "artist": "",
        "album": "",
        "title": "Hello",
        "track_number": 4,
        "fid": "https://hello",
        "album_fid": album.fid,
        "artist_fid": artist.fid,
        "album_artist_fid": album.artist.fid,
    }

    mocker.patch("funkwhale_api.music.metadata.Metadata.all", return_value=metadata)

    track = tasks.get_track_from_import_metadata(metadata)

    assert track.title == metadata["title"]
    assert track.fid == metadata["fid"]
    assert track.position == 4
    assert track.album == album
    assert track.artist == artist


def test_can_create_track_from_file_metadata_federation(factories, mocker, r_mock):
    metadata = {
        "artist": "Artist",
        "album": "Album",
        "album_artist": "Album artist",
        "title": "Hello",
        "track_number": 4,
        "fid": "https://hello",
        "album_fid": "https://album.fid",
        "artist_fid": "https://artist.fid",
        "album_artist_fid": "https://album.artist.fid",
        "fdate": timezone.now(),
        "album_fdate": timezone.now(),
        "album_artist_fdate": timezone.now(),
        "artist_fdate": timezone.now(),
        "cover_data": {"url": "https://cover/hello.png", "mimetype": "image/png"},
    }
    r_mock.get(metadata["cover_data"]["url"], body=io.BytesIO(b"coucou"))
    mocker.patch("funkwhale_api.music.metadata.Metadata.all", return_value=metadata)

    track = tasks.get_track_from_import_metadata(metadata)

    assert track.title == metadata["title"]
    assert track.fid == metadata["fid"]
    assert track.creation_date == metadata["fdate"]
    assert track.position == 4
    assert track.album.cover.read() == b"coucou"
    assert track.album.cover.path.endswith(".png")
    assert track.album.fid == metadata["album_fid"]
    assert track.album.title == metadata["album"]
    assert track.album.creation_date == metadata["album_fdate"]
    assert track.album.artist.fid == metadata["album_artist_fid"]
    assert track.album.artist.name == metadata["album_artist"]
    assert track.album.artist.creation_date == metadata["album_artist_fdate"]
    assert track.artist.fid == metadata["artist_fid"]
    assert track.artist.name == metadata["artist"]
    assert track.artist.creation_date == metadata["artist_fdate"]


def test_sort_candidates(factories):
    artist1 = factories["music.Artist"].build(fid=None, mbid=None)
    artist2 = factories["music.Artist"].build(fid=None)
    artist3 = factories["music.Artist"].build(mbid=None)
    result = tasks.sort_candidates([artist1, artist2, artist3], ["mbid", "fid"])

    assert result == [artist2, artist3, artist1]


def test_upload_import(now, factories, temp_signal, mocker):
    outbox = mocker.patch("funkwhale_api.federation.routes.outbox.dispatch")
    track = factories["music.Track"]()
    upload = factories["music.Upload"](
        track=None, import_metadata={"funkwhale": {"track": {"uuid": str(track.uuid)}}}
    )

    with temp_signal(signals.upload_import_status_updated) as handler:
        tasks.process_upload(upload_id=upload.pk)

    upload.refresh_from_db()

    assert upload.track == track
    assert upload.import_status == "finished"
    assert upload.import_date == now
    handler.assert_called_once_with(
        upload=upload,
        old_status="pending",
        new_status="finished",
        sender=None,
        signal=signals.upload_import_status_updated,
    )
    outbox.assert_called_once_with(
        {"type": "Create", "object": {"type": "Audio"}}, context={"upload": upload}
    )


def test_upload_import_get_audio_data(factories, mocker):
    mocker.patch(
        "funkwhale_api.music.models.Upload.get_audio_data",
        return_value={"size": 23, "duration": 42, "bitrate": 66},
    )
    track = factories["music.Track"]()
    upload = factories["music.Upload"](
        track=None, import_metadata={"funkwhale": {"track": {"uuid": track.uuid}}}
    )

    tasks.process_upload(upload_id=upload.pk)

    upload.refresh_from_db()
    assert upload.size == 23
    assert upload.duration == 42
    assert upload.bitrate == 66


def test_upload_import_in_place(factories, mocker):
    mocker.patch(
        "funkwhale_api.music.models.Upload.get_audio_data",
        return_value={"size": 23, "duration": 42, "bitrate": 66},
    )
    track = factories["music.Track"]()
    path = os.path.join(DATA_DIR, "test.ogg")
    upload = factories["music.Upload"](
        track=None,
        audio_file=None,
        source="file://{}".format(path),
        import_metadata={"funkwhale": {"track": {"uuid": track.uuid}}},
    )

    tasks.process_upload(upload_id=upload.pk)

    upload.refresh_from_db()
    assert upload.size == 23
    assert upload.duration == 42
    assert upload.bitrate == 66
    assert upload.mimetype == "audio/ogg"


def test_upload_import_skip_existing_track_in_own_library(factories, temp_signal):
    track = factories["music.Track"]()
    library = factories["music.Library"]()
    existing = factories["music.Upload"](
        track=track,
        import_status="finished",
        library=library,
        import_metadata={"funkwhale": {"track": {"uuid": track.mbid}}},
    )
    duplicate = factories["music.Upload"](
        track=track,
        import_status="pending",
        library=library,
        import_metadata={"funkwhale": {"track": {"uuid": track.uuid}}},
    )
    with temp_signal(signals.upload_import_status_updated) as handler:
        tasks.process_upload(upload_id=duplicate.pk)

    duplicate.refresh_from_db()

    assert duplicate.import_status == "skipped"
    assert duplicate.import_details == {
        "code": "already_imported_in_owned_libraries",
        "duplicates": [str(existing.uuid)],
    }

    handler.assert_called_once_with(
        upload=duplicate,
        old_status="pending",
        new_status="skipped",
        sender=None,
        signal=signals.upload_import_status_updated,
    )


def test_upload_import_track_uuid(now, factories):
    track = factories["music.Track"]()
    upload = factories["music.Upload"](
        track=None, import_metadata={"funkwhale": {"track": {"uuid": track.uuid}}}
    )

    tasks.process_upload(upload_id=upload.pk)

    upload.refresh_from_db()

    assert upload.track == track
    assert upload.import_status == "finished"
    assert upload.import_date == now


def test_upload_import_skip_federation(now, factories, mocker):
    outbox = mocker.patch("funkwhale_api.federation.routes.outbox.dispatch")
    track = factories["music.Track"]()
    upload = factories["music.Upload"](
        track=None,
        import_metadata={
            "funkwhale": {
                "track": {"uuid": track.uuid},
                "config": {"dispatch_outbox": False},
            }
        },
    )

    tasks.process_upload(upload_id=upload.pk)

    outbox.assert_not_called()


def test_upload_import_skip_broadcast(now, factories, mocker):
    group_send = mocker.patch("funkwhale_api.common.channels.group_send")
    track = factories["music.Track"]()
    upload = factories["music.Upload"](
        library__actor__local=True,
        track=None,
        import_metadata={
            "funkwhale": {"track": {"uuid": track.uuid}, "config": {"broadcast": False}}
        },
    )

    tasks.process_upload(upload_id=upload.pk)

    group_send.assert_not_called()


def test_upload_import_error(factories, now, temp_signal):
    upload = factories["music.Upload"](
        import_metadata={"funkwhale": {"track": {"uuid": uuid.uuid4()}}}
    )
    with temp_signal(signals.upload_import_status_updated) as handler:
        tasks.process_upload(upload_id=upload.pk)
    upload.refresh_from_db()

    assert upload.import_status == "errored"
    assert upload.import_date == now
    assert upload.import_details == {"error_code": "track_uuid_not_found"}
    handler.assert_called_once_with(
        upload=upload,
        old_status="pending",
        new_status="errored",
        sender=None,
        signal=signals.upload_import_status_updated,
    )


def test_upload_import_updates_cover_if_no_cover(factories, mocker, now):
    mocked_update = mocker.patch("funkwhale_api.music.tasks.update_album_cover")
    album = factories["music.Album"](cover="")
    track = factories["music.Track"](album=album)
    upload = factories["music.Upload"](
        track=None, import_metadata={"funkwhale": {"track": {"uuid": track.uuid}}}
    )
    tasks.process_upload(upload_id=upload.pk)
    mocked_update.assert_called_once_with(album, source=None, cover_data=None)


def test_update_album_cover_mbid(factories, mocker):
    album = factories["music.Album"](cover="")

    mocked_get = mocker.patch("funkwhale_api.music.models.Album.get_image")
    tasks.update_album_cover(album=album)

    mocked_get.assert_called_once_with()


def test_update_album_cover_file_data(factories, mocker):
    album = factories["music.Album"](cover="", mbid=None)

    mocked_get = mocker.patch("funkwhale_api.music.models.Album.get_image")
    tasks.update_album_cover(album=album, cover_data={"hello": "world"})
    mocked_get.assert_called_once_with(data={"hello": "world"})


@pytest.mark.parametrize("ext,mimetype", [("jpg", "image/jpeg"), ("png", "image/png")])
def test_update_album_cover_file_cover_separate_file(ext, mimetype, factories, mocker):
    mocker.patch("funkwhale_api.music.tasks.IMAGE_TYPES", [(ext, mimetype)])
    image_path = os.path.join(DATA_DIR, "cover.{}".format(ext))
    with open(image_path, "rb") as f:
        image_content = f.read()
    album = factories["music.Album"](cover="", mbid=None)

    mocked_get = mocker.patch("funkwhale_api.music.models.Album.get_image")
    mocker.patch("funkwhale_api.music.metadata.Metadata.get_picture", return_value=None)
    tasks.update_album_cover(album=album, source="file://" + image_path)
    mocked_get.assert_called_once_with(
        data={"mimetype": mimetype, "content": image_content}
    )


def test_federation_audio_track_to_metadata(now):
    published = now
    released = now.date()
    payload = {
        "@context": jsonld.get_default_context(),
        "type": "Track",
        "id": "http://hello.track",
        "musicbrainzId": str(uuid.uuid4()),
        "name": "Black in back",
        "position": 5,
        "disc": 2,
        "published": published.isoformat(),
        "license": "http://creativecommons.org/licenses/by-sa/4.0/",
        "copyright": "2018 Someone",
        "album": {
            "published": published.isoformat(),
            "type": "Album",
            "id": "http://hello.album",
            "name": "Purple album",
            "musicbrainzId": str(uuid.uuid4()),
            "released": released.isoformat(),
            "artists": [
                {
                    "type": "Artist",
                    "published": published.isoformat(),
                    "id": "http://hello.artist",
                    "name": "John Smith",
                    "musicbrainzId": str(uuid.uuid4()),
                }
            ],
            "cover": {
                "type": "Link",
                "href": "http://cover.test",
                "mediaType": "image/png",
            },
        },
        "artists": [
            {
                "published": published.isoformat(),
                "type": "Artist",
                "id": "http://hello.trackartist",
                "name": "Bob Smith",
                "musicbrainzId": str(uuid.uuid4()),
            }
        ],
    }
    serializer = federation_serializers.TrackSerializer(data=payload)
    serializer.is_valid(raise_exception=True)
    expected = {
        "artist": payload["artists"][0]["name"],
        "album": payload["album"]["name"],
        "album_artist": payload["album"]["artists"][0]["name"],
        "title": payload["name"],
        "date": released,
        "track_number": payload["position"],
        "disc_number": payload["disc"],
        "license": "http://creativecommons.org/licenses/by-sa/4.0/",
        "copyright": "2018 Someone",
        # musicbrainz
        "musicbrainz_albumid": payload["album"]["musicbrainzId"],
        "musicbrainz_recordingid": payload["musicbrainzId"],
        "musicbrainz_artistid": payload["artists"][0]["musicbrainzId"],
        "musicbrainz_albumartistid": payload["album"]["artists"][0]["musicbrainzId"],
        # federation
        "fid": payload["id"],
        "album_fid": payload["album"]["id"],
        "artist_fid": payload["artists"][0]["id"],
        "album_artist_fid": payload["album"]["artists"][0]["id"],
        "fdate": serializer.validated_data["published"],
        "artist_fdate": serializer.validated_data["artists"][0]["published"],
        "album_artist_fdate": serializer.validated_data["album"]["artists"][0][
            "published"
        ],
        "album_fdate": serializer.validated_data["album"]["published"],
        "cover_data": {
            "mimetype": serializer.validated_data["album"]["cover"]["mediaType"],
            "url": serializer.validated_data["album"]["cover"]["href"],
        },
    }

    result = tasks.federation_audio_track_to_metadata(serializer.validated_data)
    assert result == expected

    # ensure we never forget to test a mandatory field
    for k in metadata.ALL_FIELDS:
        assert k in result


def test_scan_library_fetches_page_and_calls_scan_page(now, mocker, factories, r_mock):
    scan = factories["music.LibraryScan"]()
    collection_conf = {
        "actor": scan.library.actor,
        "id": scan.library.fid,
        "page_size": 10,
        "items": range(10),
        "type": "Library",
        "name": "hello",
    }
    collection = federation_serializers.PaginatedCollectionSerializer(collection_conf)
    data = collection.data
    data["followers"] = "https://followers.domain"

    scan_page = mocker.patch("funkwhale_api.music.tasks.scan_library_page.delay")
    r_mock.get(collection_conf["id"], json=data)
    tasks.start_library_scan(library_scan_id=scan.pk)

    scan_page.assert_called_once_with(library_scan_id=scan.pk, page_url=data["first"])
    scan.refresh_from_db()

    assert scan.status == "scanning"
    assert scan.total_files == len(collection_conf["items"])
    assert scan.modification_date == now


def test_scan_page_fetches_page_and_creates_tracks(now, mocker, factories, r_mock):
    scan_page = mocker.patch("funkwhale_api.music.tasks.scan_library_page.delay")
    scan = factories["music.LibraryScan"](status="scanning", total_files=5)
    uploads = [
        factories["music.Upload"].build(
            fid="https://track.test/{}".format(i),
            size=42,
            bitrate=66,
            duration=99,
            library=scan.library,
        )
        for i in range(5)
    ]

    page_conf = {
        "actor": scan.library.actor,
        "id": scan.library.fid,
        "page": Paginator(uploads, 3).page(1),
        "item_serializer": federation_serializers.UploadSerializer,
    }
    page = federation_serializers.CollectionPageSerializer(page_conf)
    r_mock.get(page.data["id"], json=page.data)

    tasks.scan_library_page(library_scan_id=scan.pk, page_url=page.data["id"])

    scan.refresh_from_db()
    lts = list(scan.library.uploads.all().order_by("-creation_date"))

    assert len(lts) == 3
    for upload in uploads[:3]:
        scan.library.uploads.get(fid=upload.fid)

    assert scan.status == "scanning"
    assert scan.processed_files == 3
    assert scan.modification_date == now

    scan_page.assert_called_once_with(
        library_scan_id=scan.pk, page_url=page.data["next"]
    )


def test_scan_page_trigger_next_page_scan_skip_if_same(mocker, factories, r_mock):
    patched_scan = mocker.patch("funkwhale_api.music.tasks.scan_library_page.delay")
    scan = factories["music.LibraryScan"](status="scanning", total_files=5)
    uploads = factories["music.Upload"].build_batch(size=5, library=scan.library)
    page_conf = {
        "actor": scan.library.actor,
        "id": scan.library.fid,
        "page": Paginator(uploads, 3).page(1),
        "item_serializer": federation_serializers.UploadSerializer,
    }
    page = federation_serializers.CollectionPageSerializer(page_conf)
    data = page.data
    data["next"] = data["id"]
    r_mock.get(page.data["id"], json=data)

    tasks.scan_library_page(library_scan_id=scan.pk, page_url=data["id"])
    patched_scan.assert_not_called()
    scan.refresh_from_db()

    assert scan.status == "finished"


def test_clean_transcoding_cache(preferences, now, factories):
    preferences["music__transcoding_cache_duration"] = 60
    u1 = factories["music.UploadVersion"](
        accessed_date=now - datetime.timedelta(minutes=61)
    )
    u2 = factories["music.UploadVersion"](
        accessed_date=now - datetime.timedelta(minutes=59)
    )

    tasks.clean_transcoding_cache()

    u2.refresh_from_db()

    with pytest.raises(u1.__class__.DoesNotExist):
        u1.refresh_from_db()
