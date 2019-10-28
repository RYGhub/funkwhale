import datetime
import io
import os
import pytest
import uuid

from django.core.paginator import Paginator
from django.utils import timezone

from funkwhale_api.federation import serializers as federation_serializers
from funkwhale_api.federation import jsonld
from funkwhale_api.music import licenses, metadata, models, signals, tasks

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


# DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")


def test_can_create_track_from_file_metadata_no_mbid(db, mocker):
    add_tags = mocker.patch("funkwhale_api.tags.models.add_tags")
    metadata = {
        "title": "Test track",
        "artists": [{"name": "Test artist"}],
        "album": {"title": "Test album", "release_date": datetime.date(2012, 8, 15)},
        "position": 4,
        "disc_number": 2,
        "license": "Hello world: http://creativecommons.org/licenses/by-sa/4.0/",
        "copyright": "2018 Someone",
        "tags": ["Punk", "Rock"],
    }
    match_license = mocker.spy(licenses, "match")

    track = tasks.get_track_from_import_metadata(metadata)

    assert track.title == metadata["title"]
    assert track.mbid is None
    assert track.position == 4
    assert track.disc_number == 2
    assert track.license.code == "cc-by-sa-4.0"
    assert track.copyright == metadata["copyright"]
    assert track.album.title == metadata["album"]["title"]
    assert track.album.mbid is None
    assert track.album.release_date == datetime.date(2012, 8, 15)
    assert track.artist.name == metadata["artists"][0]["name"]
    assert track.artist.mbid is None
    assert track.artist.attributed_to is None
    match_license.assert_called_once_with(metadata["license"], metadata["copyright"])
    add_tags.assert_any_call(track, *metadata["tags"])
    add_tags.assert_any_call(track.artist, *[])
    add_tags.assert_any_call(track.album, *[])


def test_can_create_track_from_file_metadata_attributed_to(factories, mocker):
    actor = factories["federation.Actor"]()
    metadata = {
        "title": "Test track",
        "artists": [{"name": "Test artist"}],
        "album": {"title": "Test album", "release_date": datetime.date(2012, 8, 15)},
        "position": 4,
        "disc_number": 2,
        "copyright": "2018 Someone",
    }

    track = tasks.get_track_from_import_metadata(metadata, attributed_to=actor)

    assert track.title == metadata["title"]
    assert track.mbid is None
    assert track.position == 4
    assert track.disc_number == 2
    assert track.copyright == metadata["copyright"]
    assert track.attributed_to == actor
    assert track.album.title == metadata["album"]["title"]
    assert track.album.mbid is None
    assert track.album.release_date == datetime.date(2012, 8, 15)
    assert track.album.attributed_to == actor
    assert track.artist.name == metadata["artists"][0]["name"]
    assert track.artist.mbid is None
    assert track.artist.attributed_to == actor


def test_can_create_track_from_file_metadata_truncates_too_long_values(
    factories, mocker
):
    metadata = {
        "title": "a" * 5000,
        "artists": [{"name": "b" * 5000}],
        "album": {"title": "c" * 5000, "release_date": datetime.date(2012, 8, 15)},
        "position": 4,
        "disc_number": 2,
        "copyright": "d" * 5000,
    }

    track = tasks.get_track_from_import_metadata(metadata)

    assert track.title == metadata["title"][: models.MAX_LENGTHS["TRACK_TITLE"]]
    assert track.copyright == metadata["copyright"][: models.MAX_LENGTHS["COPYRIGHT"]]
    assert (
        track.album.title
        == metadata["album"]["title"][: models.MAX_LENGTHS["ALBUM_TITLE"]]
    )
    assert (
        track.artist.name
        == metadata["artists"][0]["name"][: models.MAX_LENGTHS["ARTIST_NAME"]]
    )


def test_can_create_track_from_file_metadata_featuring(factories):
    metadata = {
        "title": "Whole Lotta Love",
        "position": 1,
        "disc_number": 1,
        "mbid": "508704c0-81d4-4c94-ba58-3fc0b7da23eb",
        "album": {
            "title": "Guitar Heaven: The Greatest Guitar Classics of All Time",
            "mbid": "d06f2072-4148-488d-af6f-69ab6539ddb8",
            "release_date": datetime.date(2010, 9, 17),
            "artists": [
                {"name": "Santana", "mbid": "9a3bf45c-347d-4630-894d-7cf3e8e0b632"}
            ],
        },
        "artists": [{"name": "Santana feat. Chris Cornell", "mbid": None}],
    }
    track = tasks.get_track_from_import_metadata(metadata)

    assert track.album.artist.name == "Santana"
    assert track.artist.name == "Santana feat. Chris Cornell"


def test_can_create_track_from_file_metadata_mbid(factories, mocker):
    metadata = {
        "title": "Test track",
        "artists": [
            {"name": "Test artist", "mbid": "9c6bddde-6228-4d9f-ad0d-03f6fcb19e13"}
        ],
        "album": {
            "title": "Test album",
            "release_date": datetime.date(2012, 8, 15),
            "mbid": "9c6bddde-6478-4d9f-ad0d-03f6fcb19e15",
            "artists": [
                {
                    "name": "Test album artist",
                    "mbid": "9c6bddde-6478-4d9f-ad0d-03f6fcb19e13",
                }
            ],
        },
        "position": 4,
        "mbid": "f269d497-1cc0-4ae4-a0c4-157ec7d73fcb",
        "cover_data": {"content": b"image_content", "mimetype": "image/png"},
    }

    track = tasks.get_track_from_import_metadata(metadata)

    assert track.title == metadata["title"]
    assert track.mbid == metadata["mbid"]
    assert track.position == 4
    assert track.disc_number is None
    assert track.album.title == metadata["album"]["title"]
    assert track.album.mbid == metadata["album"]["mbid"]
    assert track.album.artist.mbid == metadata["album"]["artists"][0]["mbid"]
    assert track.album.artist.name == metadata["album"]["artists"][0]["name"]
    assert track.album.release_date == datetime.date(2012, 8, 15)
    assert track.artist.name == metadata["artists"][0]["name"]
    assert track.artist.mbid == metadata["artists"][0]["mbid"]


def test_can_create_track_from_file_metadata_mbid_existing_album_artist(
    factories, mocker
):
    artist = factories["music.Artist"]()
    album = factories["music.Album"]()
    metadata = {
        "album": {
            "mbid": album.mbid,
            "title": "",
            "artists": [{"name": "", "mbid": album.artist.mbid}],
        },
        "title": "Hello",
        "position": 4,
        "artists": [{"mbid": artist.mbid, "name": ""}],
        "mbid": "f269d497-1cc0-4ae4-a0c4-157ec7d73fcb",
    }

    track = tasks.get_track_from_import_metadata(metadata)

    assert track.title == metadata["title"]
    assert track.mbid == metadata["mbid"]
    assert track.position == 4
    assert track.album == album
    assert track.artist == artist


def test_can_create_track_from_file_metadata_fid_existing_album_artist(
    factories, mocker
):
    artist = factories["music.Artist"]()
    album = factories["music.Album"]()
    metadata = {
        "artists": [{"name": "", "fid": artist.fid}],
        "album": {
            "title": "",
            "fid": album.fid,
            "artists": [{"name": "", "fid": album.artist.fid}],
        },
        "title": "Hello",
        "position": 4,
        "fid": "https://hello",
    }

    track = tasks.get_track_from_import_metadata(metadata)

    assert track.title == metadata["title"]
    assert track.fid == metadata["fid"]
    assert track.position == 4
    assert track.album == album
    assert track.artist == artist


def test_can_create_track_from_file_metadata_distinct_release_mbid(factories):
    """Cf https://dev.funkwhale.audio/funkwhale/funkwhale/issues/772"""
    artist = factories["music.Artist"]()
    album = factories["music.Album"](artist=artist)
    track = factories["music.Track"](album=album, artist=artist)
    metadata = {
        "artists": [{"name": artist.name, "mbid": artist.mbid}],
        "album": {"title": album.title, "mbid": str(uuid.uuid4())},
        "title": track.title,
        "position": 4,
        "fid": "https://hello",
    }

    new_track = tasks.get_track_from_import_metadata(metadata)

    # the returned track should be different from the existing one, and mapped
    # to a new album, because the albumid is different
    assert new_track.album != album
    assert new_track != track


def test_can_create_track_from_file_metadata_distinct_position(factories):
    """Cf https://dev.funkwhale.audio/funkwhale/funkwhale/issues/740"""
    artist = factories["music.Artist"]()
    album = factories["music.Album"](artist=artist)
    track = factories["music.Track"](album=album, artist=artist)
    metadata = {
        "artists": [{"name": artist.name, "mbid": artist.mbid}],
        "album": {"title": album.title, "mbid": album.mbid},
        "title": track.title,
        "position": track.position + 1,
    }

    new_track = tasks.get_track_from_import_metadata(metadata)

    assert new_track != track


def test_can_create_track_from_file_metadata_federation(factories, mocker, r_mock):
    metadata = {
        "artists": [
            {"name": "Artist", "fid": "https://artist.fid", "fdate": timezone.now()}
        ],
        "album": {
            "title": "Album",
            "fid": "https://album.fid",
            "fdate": timezone.now(),
            "artists": [
                {
                    "name": "Album artist",
                    "fid": "https://album.artist.fid",
                    "fdate": timezone.now(),
                }
            ],
        },
        "title": "Hello",
        "position": 4,
        "fid": "https://hello",
        "fdate": timezone.now(),
        "cover_data": {"url": "https://cover/hello.png", "mimetype": "image/png"},
    }
    r_mock.get(metadata["cover_data"]["url"], body=io.BytesIO(b"coucou"))

    track = tasks.get_track_from_import_metadata(metadata, update_cover=True)

    assert track.title == metadata["title"]
    assert track.fid == metadata["fid"]
    assert track.creation_date == metadata["fdate"]
    assert track.position == 4
    assert track.album.cover.read() == b"coucou"
    assert track.album.cover_path.endswith(".png")
    assert track.album.fid == metadata["album"]["fid"]
    assert track.album.title == metadata["album"]["title"]
    assert track.album.creation_date == metadata["album"]["fdate"]
    assert track.album.artist.fid == metadata["album"]["artists"][0]["fid"]
    assert track.album.artist.name == metadata["album"]["artists"][0]["name"]
    assert track.album.artist.creation_date == metadata["album"]["artists"][0]["fdate"]
    assert track.artist.fid == metadata["artists"][0]["fid"]
    assert track.artist.name == metadata["artists"][0]["name"]
    assert track.artist.creation_date == metadata["artists"][0]["fdate"]


def test_sort_candidates(factories):
    artist1 = factories["music.Artist"].build(fid=None, mbid=None)
    artist2 = factories["music.Artist"].build(fid=None)
    artist3 = factories["music.Artist"].build(mbid=None)
    result = tasks.sort_candidates([artist1, artist2, artist3], ["mbid", "fid"])

    assert result == [artist2, artist3, artist1]


def test_upload_import(now, factories, temp_signal, mocker):
    outbox = mocker.patch("funkwhale_api.federation.routes.outbox.dispatch")
    update_album_cover = mocker.patch("funkwhale_api.music.tasks.update_album_cover")
    get_picture = mocker.patch("funkwhale_api.music.metadata.Metadata.get_picture")
    get_track_from_import_metadata = mocker.spy(tasks, "get_track_from_import_metadata")
    track = factories["music.Track"](album__cover="")
    upload = factories["music.Upload"](
        track=None, import_metadata={"funkwhale": {"track": {"uuid": str(track.uuid)}}}
    )
    create_entries = mocker.patch(
        "funkwhale_api.music.models.TrackActor.create_entries"
    )

    with temp_signal(signals.upload_import_status_updated) as handler:
        tasks.process_upload(upload_id=upload.pk)

    upload.refresh_from_db()

    assert upload.track == track
    assert upload.import_status == "finished"
    assert upload.import_date == now
    get_picture.assert_called_once_with("cover_front", "other")
    update_album_cover.assert_called_once_with(
        upload.track.album, cover_data=get_picture.return_value, source=upload.source
    )
    assert (
        get_track_from_import_metadata.call_args[-1]["attributed_to"]
        == upload.library.actor
    )
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
    create_entries.assert_called_once_with(
        library=upload.library,
        delete_existing=False,
        upload_and_track_ids=[(upload.pk, upload.track_id)],
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
    assert upload.import_details == {
        "error_code": "track_uuid_not_found",
        "detail": None,
    }
    handler.assert_called_once_with(
        upload=upload,
        old_status="pending",
        new_status="errored",
        sender=None,
        signal=signals.upload_import_status_updated,
    )


def test_upload_import_error_metadata(factories, now, temp_signal, mocker):
    path = os.path.join(DATA_DIR, "test.ogg")
    upload = factories["music.Upload"](audio_file__frompath=path)
    mocker.patch.object(
        metadata.AlbumField,
        "to_internal_value",
        side_effect=metadata.serializers.ValidationError("Hello"),
    )
    with temp_signal(signals.upload_import_status_updated) as handler:
        tasks.process_upload(upload_id=upload.pk)
    upload.refresh_from_db()

    assert upload.import_status == "errored"
    assert upload.import_date == now
    assert upload.import_details == {
        "error_code": "invalid_metadata",
        "detail": {"album": ["Hello"]},
        "file_metadata": metadata.Metadata(path).all(),
    }
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


def test_federation_audio_track_to_metadata(now, mocker):
    published = now
    released = now.date()
    references = {
        "http://track.attributed": mocker.Mock(),
        "http://album.attributed": mocker.Mock(),
        "http://album-artist.attributed": mocker.Mock(),
        "http://artist.attributed": mocker.Mock(),
    }
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
        "attributedTo": "http://track.attributed",
        "tag": [{"type": "Hashtag", "name": "TrackTag"}],
        "album": {
            "published": published.isoformat(),
            "type": "Album",
            "id": "http://hello.album",
            "name": "Purple album",
            "musicbrainzId": str(uuid.uuid4()),
            "released": released.isoformat(),
            "tag": [{"type": "Hashtag", "name": "AlbumTag"}],
            "attributedTo": "http://album.attributed",
            "artists": [
                {
                    "type": "Artist",
                    "published": published.isoformat(),
                    "id": "http://hello.artist",
                    "name": "John Smith",
                    "musicbrainzId": str(uuid.uuid4()),
                    "attributedTo": "http://album-artist.attributed",
                    "tag": [{"type": "Hashtag", "name": "AlbumArtistTag"}],
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
                "attributedTo": "http://artist.attributed",
                "tag": [{"type": "Hashtag", "name": "ArtistTag"}],
            }
        ],
    }
    serializer = federation_serializers.TrackSerializer(data=payload)
    serializer.is_valid(raise_exception=True)
    expected = {
        "title": payload["name"],
        "position": payload["position"],
        "disc_number": payload["disc"],
        "license": "http://creativecommons.org/licenses/by-sa/4.0/",
        "copyright": "2018 Someone",
        "mbid": payload["musicbrainzId"],
        "fdate": serializer.validated_data["published"],
        "fid": payload["id"],
        "attributed_to": references["http://track.attributed"],
        "tags": ["TrackTag"],
        "album": {
            "title": payload["album"]["name"],
            "attributed_to": references["http://album.attributed"],
            "release_date": released,
            "mbid": payload["album"]["musicbrainzId"],
            "fid": payload["album"]["id"],
            "fdate": serializer.validated_data["album"]["published"],
            "tags": ["AlbumTag"],
            "artists": [
                {
                    "name": a["name"],
                    "mbid": a["musicbrainzId"],
                    "fid": a["id"],
                    "attributed_to": references["http://album-artist.attributed"],
                    "fdate": serializer.validated_data["album"]["artists"][i][
                        "published"
                    ],
                    "tags": ["AlbumArtistTag"],
                }
                for i, a in enumerate(payload["album"]["artists"])
            ],
        },
        # musicbrainz
        # federation
        "artists": [
            {
                "name": a["name"],
                "mbid": a["musicbrainzId"],
                "fid": a["id"],
                "fdate": serializer.validated_data["artists"][i]["published"],
                "attributed_to": references["http://artist.attributed"],
                "tags": ["ArtistTag"],
            }
            for i, a in enumerate(payload["artists"])
        ],
        "cover_data": {
            "mimetype": serializer.validated_data["album"]["cover"]["mediaType"],
            "url": serializer.validated_data["album"]["cover"]["href"],
        },
    }

    result = tasks.federation_audio_track_to_metadata(
        serializer.validated_data, references
    )
    assert result == expected


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


def test_get_prunable_tracks(factories):
    prunable_track = factories["music.Track"]()
    # non prunable tracks
    factories["music.Upload"]()
    factories["favorites.TrackFavorite"]()
    factories["history.Listening"]()
    factories["playlists.PlaylistTrack"]()

    assert list(tasks.get_prunable_tracks()) == [prunable_track]


def test_get_prunable_tracks_include_favorites(factories):
    prunable_track = factories["music.Track"]()
    favorited = factories["favorites.TrackFavorite"]().track
    # non prunable tracks
    factories["favorites.TrackFavorite"](track__playable=True)
    factories["music.Upload"]()
    factories["history.Listening"]()
    factories["playlists.PlaylistTrack"]()

    qs = tasks.get_prunable_tracks(exclude_favorites=False).order_by("id")
    assert list(qs) == [prunable_track, favorited]


def test_get_prunable_tracks_include_playlists(factories):
    prunable_track = factories["music.Track"]()
    in_playlist = factories["playlists.PlaylistTrack"]().track
    # non prunable tracks
    factories["favorites.TrackFavorite"]()
    factories["music.Upload"]()
    factories["history.Listening"]()
    factories["playlists.PlaylistTrack"](track__playable=True)

    qs = tasks.get_prunable_tracks(exclude_playlists=False).order_by("id")
    assert list(qs) == [prunable_track, in_playlist]


def test_get_prunable_tracks_include_listenings(factories):
    prunable_track = factories["music.Track"]()
    listened = factories["history.Listening"]().track
    # non prunable tracks
    factories["favorites.TrackFavorite"]()
    factories["music.Upload"]()
    factories["history.Listening"](track__playable=True)
    factories["playlists.PlaylistTrack"]()

    qs = tasks.get_prunable_tracks(exclude_listenings=False).order_by("id")
    assert list(qs) == [prunable_track, listened]


def test_get_prunable_albums(factories):
    prunable_album = factories["music.Album"]()
    # non prunable album
    factories["music.Track"]().album

    assert list(tasks.get_prunable_albums()) == [prunable_album]


def test_get_prunable_artists(factories):
    prunable_artist = factories["music.Artist"]()
    # non prunable artist
    non_prunable_artist = factories["music.Artist"]()
    non_prunable_album_artist = factories["music.Artist"]()
    factories["music.Track"](artist=non_prunable_artist)
    factories["music.Track"](album__artist=non_prunable_album_artist)

    assert list(tasks.get_prunable_artists()) == [prunable_artist]


def test_update_library_entity(factories, mocker):
    artist = factories["music.Artist"]()
    save = mocker.spy(artist, "save")

    tasks.update_library_entity(artist, {"name": "Hello"})
    save.assert_called_once_with(update_fields=["name"])

    artist.refresh_from_db()
    assert artist.name == "Hello"


@pytest.mark.parametrize(
    "name, ext, mimetype",
    [
        ("cover", "png", "image/png"),
        ("cover", "jpg", "image/jpeg"),
        ("cover", "jpeg", "image/jpeg"),
        ("folder", "png", "image/png"),
        ("folder", "jpg", "image/jpeg"),
        ("folder", "jpeg", "image/jpeg"),
    ],
)
def test_get_cover_from_fs(name, ext, mimetype, tmpdir):
    cover_path = os.path.join(tmpdir, "{}.{}".format(name, ext))
    content = "Hello"
    with open(cover_path, "w") as f:
        f.write(content)

    expected = {"mimetype": mimetype, "content": content.encode()}
    assert tasks.get_cover_from_fs(tmpdir) == expected


@pytest.mark.parametrize("name", ["cover.gif", "folder.gif"])
def test_get_cover_from_fs_ignored(name, tmpdir):
    cover_path = os.path.join(tmpdir, name)
    content = "Hello"
    with open(cover_path, "w") as f:
        f.write(content)

    assert tasks.get_cover_from_fs(tmpdir) is None
