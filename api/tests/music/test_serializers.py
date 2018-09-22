from funkwhale_api.music import models
from funkwhale_api.music import serializers
from funkwhale_api.music import tasks


def test_artist_album_serializer(factories, to_api_date):
    track = factories["music.Track"]()
    album = track.album
    album = album.__class__.objects.with_tracks_count().get(pk=album.pk)
    expected = {
        "id": album.id,
        "mbid": str(album.mbid),
        "title": album.title,
        "artist": album.artist.id,
        "creation_date": to_api_date(album.creation_date),
        "tracks_count": 1,
        "is_playable": None,
        "cover": {
            "original": album.cover.url,
            "square_crop": album.cover.crop["400x400"].url,
            "medium_square_crop": album.cover.crop["200x200"].url,
            "small_square_crop": album.cover.crop["50x50"].url,
        },
        "release_date": to_api_date(album.release_date),
    }
    serializer = serializers.ArtistAlbumSerializer(album)

    assert serializer.data == expected


def test_artist_with_albums_serializer(factories, to_api_date):
    track = factories["music.Track"]()
    artist = track.artist
    artist = artist.__class__.objects.with_albums().get(pk=artist.pk)
    album = list(artist.albums.all())[0]

    expected = {
        "id": artist.id,
        "mbid": str(artist.mbid),
        "name": artist.name,
        "creation_date": to_api_date(artist.creation_date),
        "albums": [serializers.ArtistAlbumSerializer(album).data],
    }
    serializer = serializers.ArtistWithAlbumsSerializer(artist)
    assert serializer.data == expected


def test_album_track_serializer(factories, to_api_date):
    upload = factories["music.Upload"]()
    track = upload.track

    expected = {
        "id": track.id,
        "artist": serializers.ArtistSimpleSerializer(track.artist).data,
        "album": track.album.id,
        "mbid": str(track.mbid),
        "title": track.title,
        "position": track.position,
        "is_playable": None,
        "creation_date": to_api_date(track.creation_date),
        "listen_url": track.listen_url,
        "duration": None,
    }
    serializer = serializers.AlbumTrackSerializer(track)
    assert serializer.data == expected


def test_upload_serializer(factories, to_api_date):
    upload = factories["music.Upload"]()

    expected = {
        "uuid": str(upload.uuid),
        "filename": upload.filename,
        "track": serializers.TrackSerializer(upload.track).data,
        "duration": upload.duration,
        "mimetype": upload.mimetype,
        "bitrate": upload.bitrate,
        "size": upload.size,
        "library": serializers.LibraryForOwnerSerializer(upload.library).data,
        "creation_date": upload.creation_date.isoformat().split("+")[0] + "Z",
        "import_date": None,
        "import_status": "pending",
    }
    serializer = serializers.UploadSerializer(upload)
    assert serializer.data == expected


def test_upload_owner_serializer(factories, to_api_date):
    upload = factories["music.Upload"](
        import_status="success",
        import_details={"hello": "world"},
        import_metadata={"import": "metadata"},
        import_reference="ref",
        metadata={"test": "metadata"},
        source="upload://test",
    )

    expected = {
        "uuid": str(upload.uuid),
        "filename": upload.filename,
        "track": serializers.TrackSerializer(upload.track).data,
        "duration": upload.duration,
        "mimetype": upload.mimetype,
        "bitrate": upload.bitrate,
        "size": upload.size,
        "library": serializers.LibraryForOwnerSerializer(upload.library).data,
        "creation_date": upload.creation_date.isoformat().split("+")[0] + "Z",
        "metadata": {"test": "metadata"},
        "import_metadata": {"import": "metadata"},
        "import_date": None,
        "import_status": "success",
        "import_details": {"hello": "world"},
        "source": "upload://test",
        "import_reference": "ref",
    }
    serializer = serializers.UploadForOwnerSerializer(upload)
    assert serializer.data == expected


def test_album_serializer(factories, to_api_date):
    track1 = factories["music.Track"](position=2)
    track2 = factories["music.Track"](position=1, album=track1.album)
    album = track1.album
    expected = {
        "id": album.id,
        "mbid": str(album.mbid),
        "title": album.title,
        "artist": serializers.ArtistSimpleSerializer(album.artist).data,
        "creation_date": to_api_date(album.creation_date),
        "is_playable": None,
        "cover": {
            "original": album.cover.url,
            "square_crop": album.cover.crop["400x400"].url,
            "medium_square_crop": album.cover.crop["200x200"].url,
            "small_square_crop": album.cover.crop["50x50"].url,
        },
        "release_date": to_api_date(album.release_date),
        "tracks": serializers.AlbumTrackSerializer([track2, track1], many=True).data,
    }
    serializer = serializers.AlbumSerializer(album)

    assert serializer.data == expected


def test_track_serializer(factories, to_api_date):
    upload = factories["music.Upload"]()
    track = upload.track

    expected = {
        "id": track.id,
        "artist": serializers.ArtistSimpleSerializer(track.artist).data,
        "album": serializers.TrackAlbumSerializer(track.album).data,
        "mbid": str(track.mbid),
        "title": track.title,
        "position": track.position,
        "is_playable": None,
        "creation_date": to_api_date(track.creation_date),
        "lyrics": track.get_lyrics_url(),
        "listen_url": track.listen_url,
        "duration": None,
        "size": None,
        "bitrate": None,
        "mimetype": None,
    }
    serializer = serializers.TrackSerializer(track)
    assert serializer.data == expected


def test_user_cannot_bind_file_to_a_not_owned_library(factories):
    user = factories["users.User"]()
    library = factories["music.Library"]()

    s = serializers.UploadForOwnerSerializer(
        data={"library": library.uuid, "source": "upload://test"},
        context={"user": user},
    )
    assert s.is_valid() is False
    assert "library" in s.errors


def test_user_can_create_file_in_own_library(factories, uploaded_audio_file):
    user = factories["users.User"]()
    library = factories["music.Library"](actor__user=user)
    s = serializers.UploadForOwnerSerializer(
        data={
            "library": library.uuid,
            "source": "upload://test",
            "audio_file": uploaded_audio_file,
        },
        context={"user": user},
    )
    assert s.is_valid(raise_exception=True) is True
    upload = s.save()

    assert upload.library == library


def test_create_file_checks_for_user_quota(
    factories, preferences, uploaded_audio_file, mocker
):
    mocker.patch(
        "funkwhale_api.users.models.User.get_quota_status",
        return_value={"remaining": 0},
    )
    user = factories["users.User"]()
    library = factories["music.Library"](actor__user=user)
    s = serializers.UploadForOwnerSerializer(
        data={
            "library": library.uuid,
            "source": "upload://test",
            "audio_file": uploaded_audio_file,
        },
        context={"user": user},
    )
    assert s.is_valid() is False
    assert s.errors["non_field_errors"] == ["upload_quota_reached"]


def test_manage_upload_action_delete(factories, queryset_equal_list, mocker):
    dispatch = mocker.patch("funkwhale_api.federation.routes.outbox.dispatch")
    library1 = factories["music.Library"]()
    library2 = factories["music.Library"]()
    library1_uploads = factories["music.Upload"].create_batch(size=3, library=library1)
    library2_uploads = factories["music.Upload"].create_batch(size=3, library=library2)
    s = serializers.UploadActionSerializer(queryset=None)

    s.handle_delete(library1_uploads[0].__class__.objects.all())

    assert library1_uploads[0].__class__.objects.count() == 0
    dispatch.assert_any_call(
        {"type": "Delete", "object": {"type": "Audio"}},
        context={"uploads": library1_uploads},
    )
    dispatch.assert_any_call(
        {"type": "Delete", "object": {"type": "Audio"}},
        context={"uploads": library2_uploads},
    )


def test_manage_upload_action_relaunch_import(factories, mocker):
    m = mocker.patch("funkwhale_api.common.utils.on_commit")

    # this one is finished and should stay as is
    finished = factories["music.Upload"](import_status="finished")

    to_relaunch = [
        factories["music.Upload"](import_status="pending"),
        factories["music.Upload"](import_status="skipped"),
        factories["music.Upload"](import_status="errored"),
    ]
    s = serializers.UploadActionSerializer(queryset=None)

    s.handle_relaunch_import(models.Upload.objects.all())

    for obj in to_relaunch:
        obj.refresh_from_db()
        assert obj.import_status == "pending"
        m.assert_any_call(tasks.import_upload.delay, upload_id=obj.pk)

    finished.refresh_from_db()
    assert finished.import_status == "finished"
    assert m.call_count == 3
