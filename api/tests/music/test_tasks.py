import datetime
import os
import pytest
import uuid

from django.core.paginator import Paginator

from funkwhale_api.federation import serializers as federation_serializers
from funkwhale_api.music import signals, tasks

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


# DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")


def test_can_create_track_from_file_metadata_no_mbid(db, mocker):
    metadata = {
        "artist": ["Test artist"],
        "album": ["Test album"],
        "title": ["Test track"],
        "TRACKNUMBER": ["4"],
        "date": ["2012-08-15"],
    }
    mocker.patch("mutagen.File", return_value=metadata)
    mocker.patch(
        "funkwhale_api.music.metadata.Metadata.get_file_type", return_value="OggVorbis"
    )
    track = tasks.import_track_data_from_file(os.path.join(DATA_DIR, "dummy_file.ogg"))

    assert track.title == metadata["title"][0]
    assert track.mbid is None
    assert track.position == 4
    assert track.album.title == metadata["album"][0]
    assert track.album.mbid is None
    assert track.album.release_date == datetime.date(2012, 8, 15)
    assert track.artist.name == metadata["artist"][0]
    assert track.artist.mbid is None


def test_can_create_track_from_file_metadata_mbid(factories, mocker):
    album = factories["music.Album"]()
    artist = factories["music.Artist"]()
    mocker.patch(
        "funkwhale_api.music.models.Album.get_or_create_from_api",
        return_value=(album, True),
    )

    album_data = {
        "release": {
            "id": album.mbid,
            "medium-list": [
                {
                    "track-list": [
                        {
                            "id": "03baca8b-855a-3c05-8f3d-d3235287d84d",
                            "position": "4",
                            "number": "4",
                            "recording": {
                                "id": "2109e376-132b-40ad-b993-2bb6812e19d4",
                                "title": "Teen Age Riot",
                                "artist-credit": [
                                    {"artist": {"id": artist.mbid, "name": artist.name}}
                                ],
                            },
                        }
                    ],
                    "track-count": 1,
                }
            ],
        }
    }
    mocker.patch("funkwhale_api.musicbrainz.api.releases.get", return_value=album_data)
    track_data = album_data["release"]["medium-list"][0]["track-list"][0]
    metadata = {
        "musicbrainz_albumid": [album.mbid],
        "musicbrainz_trackid": [track_data["recording"]["id"]],
    }
    mocker.patch("mutagen.File", return_value=metadata)
    mocker.patch(
        "funkwhale_api.music.metadata.Metadata.get_file_type", return_value="OggVorbis"
    )
    track = tasks.import_track_data_from_file(os.path.join(DATA_DIR, "dummy_file.ogg"))

    assert track.title == track_data["recording"]["title"]
    assert track.mbid == track_data["recording"]["id"]
    assert track.position == 4
    assert track.album == album
    assert track.artist == artist


def test_upload_import_mbid(now, factories, temp_signal, mocker):
    outbox = mocker.patch("funkwhale_api.federation.routes.outbox.dispatch")
    track = factories["music.Track"]()
    upload = factories["music.Upload"](
        track=None, import_metadata={"track": {"mbid": track.mbid}}
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
        track=None, import_metadata={"track": {"mbid": track.mbid}}
    )

    tasks.process_upload(upload_id=upload.pk)

    upload.refresh_from_db()
    assert upload.size == 23
    assert upload.duration == 42
    assert upload.bitrate == 66


def test_upload_import_skip_existing_track_in_own_library(factories, temp_signal):
    track = factories["music.Track"]()
    library = factories["music.Library"]()
    existing = factories["music.Upload"](
        track=track,
        import_status="finished",
        library=library,
        import_metadata={"track": {"mbid": track.mbid}},
    )
    duplicate = factories["music.Upload"](
        track=track,
        import_status="pending",
        library=library,
        import_metadata={"track": {"mbid": track.mbid}},
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
        track=None, import_metadata={"track": {"uuid": track.uuid}}
    )

    tasks.process_upload(upload_id=upload.pk)

    upload.refresh_from_db()

    assert upload.track == track
    assert upload.import_status == "finished"
    assert upload.import_date == now


def test_upload_import_error(factories, now, temp_signal):
    upload = factories["music.Upload"](
        import_metadata={"track": {"uuid": uuid.uuid4()}}
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
        track=None, import_metadata={"track": {"uuid": track.uuid}}
    )
    tasks.process_upload(upload_id=upload.pk)
    mocked_update.assert_called_once_with(album, upload)


def test_update_album_cover_mbid(factories, mocker):
    album = factories["music.Album"](cover="")

    mocked_get = mocker.patch("funkwhale_api.music.models.Album.get_image")
    tasks.update_album_cover(album=album, upload=None)

    mocked_get.assert_called_once_with()


def test_update_album_cover_file_data(factories, mocker):
    album = factories["music.Album"](cover="", mbid=None)
    upload = factories["music.Upload"](track__album=album)

    mocked_get = mocker.patch("funkwhale_api.music.models.Album.get_image")
    mocker.patch(
        "funkwhale_api.music.metadata.Metadata.get_picture",
        return_value={"hello": "world"},
    )
    tasks.update_album_cover(album=album, upload=upload)
    upload.get_metadata()
    mocked_get.assert_called_once_with(data={"hello": "world"})


@pytest.mark.parametrize("ext,mimetype", [("jpg", "image/jpeg"), ("png", "image/png")])
def test_update_album_cover_file_cover_separate_file(ext, mimetype, factories, mocker):
    mocker.patch("funkwhale_api.music.tasks.IMAGE_TYPES", [(ext, mimetype)])
    image_path = os.path.join(DATA_DIR, "cover.{}".format(ext))
    with open(image_path, "rb") as f:
        image_content = f.read()
    album = factories["music.Album"](cover="", mbid=None)
    upload = factories["music.Upload"](
        track__album=album, source="file://" + image_path
    )

    mocked_get = mocker.patch("funkwhale_api.music.models.Album.get_image")
    mocker.patch("funkwhale_api.music.metadata.Metadata.get_picture", return_value=None)
    tasks.update_album_cover(album=album, upload=upload)
    upload.get_metadata()
    mocked_get.assert_called_once_with(
        data={"mimetype": mimetype, "content": image_content}
    )


def test_scan_library_fetches_page_and_calls_scan_page(now, mocker, factories, r_mock):
    scan = factories["music.LibraryScan"]()
    collection_conf = {
        "actor": scan.library.actor,
        "id": scan.library.fid,
        "page_size": 10,
        "items": range(10),
    }
    collection = federation_serializers.PaginatedCollectionSerializer(collection_conf)
    scan_page = mocker.patch("funkwhale_api.music.tasks.scan_library_page.delay")
    r_mock.get(collection_conf["id"], json=collection.data)
    tasks.start_library_scan(library_scan_id=scan.pk)

    scan_page.assert_called_once_with(
        library_scan_id=scan.pk, page_url=collection.data["first"]
    )
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
