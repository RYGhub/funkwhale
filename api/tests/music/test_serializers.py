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
    tf = factories["music.TrackFile"]()
    track = tf.track

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
    }
    serializer = serializers.AlbumTrackSerializer(track)
    assert serializer.data == expected


def test_track_file_serializer(factories, to_api_date):
    tf = factories["music.TrackFile"]()

    expected = {
        "uuid": str(tf.uuid),
        "filename": tf.filename,
        "track": serializers.TrackSerializer(tf.track).data,
        "duration": tf.duration,
        "mimetype": tf.mimetype,
        "bitrate": tf.bitrate,
        "size": tf.size,
        "library": serializers.LibraryForOwnerSerializer(tf.library).data,
        "creation_date": tf.creation_date.isoformat().split("+")[0] + "Z",
        "import_date": None,
        "import_status": "pending",
    }
    serializer = serializers.TrackFileSerializer(tf)
    assert serializer.data == expected


def test_track_file_owner_serializer(factories, to_api_date):
    tf = factories["music.TrackFile"](
        import_status="success",
        import_details={"hello": "world"},
        import_metadata={"import": "metadata"},
        import_reference="ref",
        metadata={"test": "metadata"},
        source="upload://test",
    )

    expected = {
        "uuid": str(tf.uuid),
        "filename": tf.filename,
        "track": serializers.TrackSerializer(tf.track).data,
        "duration": tf.duration,
        "mimetype": tf.mimetype,
        "bitrate": tf.bitrate,
        "size": tf.size,
        "library": serializers.LibraryForOwnerSerializer(tf.library).data,
        "creation_date": tf.creation_date.isoformat().split("+")[0] + "Z",
        "metadata": {"test": "metadata"},
        "import_metadata": {"import": "metadata"},
        "import_date": None,
        "import_status": "success",
        "import_details": {"hello": "world"},
        "source": "upload://test",
        "import_reference": "ref",
    }
    serializer = serializers.TrackFileForOwnerSerializer(tf)
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
    tf = factories["music.TrackFile"]()
    track = tf.track

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
    }
    serializer = serializers.TrackSerializer(track)
    assert serializer.data == expected


def test_user_cannot_bind_file_to_a_not_owned_library(factories):
    user = factories["users.User"]()
    library = factories["music.Library"]()

    s = serializers.TrackFileForOwnerSerializer(
        data={"library": library.uuid, "source": "upload://test"},
        context={"user": user},
    )
    assert s.is_valid() is False
    assert "library" in s.errors


def test_user_can_create_file_in_own_library(factories, uploaded_audio_file):
    user = factories["users.User"]()
    library = factories["music.Library"](actor__user=user)
    s = serializers.TrackFileForOwnerSerializer(
        data={
            "library": library.uuid,
            "source": "upload://test",
            "audio_file": uploaded_audio_file,
        },
        context={"user": user},
    )
    assert s.is_valid(raise_exception=True) is True
    tf = s.save()

    assert tf.library == library


def test_create_file_checks_for_user_quota(
    factories, preferences, uploaded_audio_file, mocker
):
    mocker.patch(
        "funkwhale_api.users.models.User.get_quota_status",
        return_value={"remaining": 0},
    )
    user = factories["users.User"]()
    library = factories["music.Library"](actor__user=user)
    s = serializers.TrackFileForOwnerSerializer(
        data={
            "library": library.uuid,
            "source": "upload://test",
            "audio_file": uploaded_audio_file,
        },
        context={"user": user},
    )
    assert s.is_valid() is False
    assert s.errors["non_field_errors"] == ["upload_quota_reached"]


def test_manage_track_file_action_delete(factories):
    tfs = factories["music.TrackFile"](size=5)
    s = serializers.TrackFileActionSerializer(queryset=None)

    s.handle_delete(tfs.__class__.objects.all())

    assert tfs.__class__.objects.count() == 0


def test_manage_track_file_action_relaunch_import(factories, mocker):
    m = mocker.patch("funkwhale_api.common.utils.on_commit")

    # this one is finished and should stay as is
    finished = factories["music.TrackFile"](import_status="finished")

    to_relaunch = [
        factories["music.TrackFile"](import_status="pending"),
        factories["music.TrackFile"](import_status="skipped"),
        factories["music.TrackFile"](import_status="errored"),
    ]
    s = serializers.TrackFileActionSerializer(queryset=None)

    s.handle_relaunch_import(models.TrackFile.objects.all())

    for obj in to_relaunch:
        obj.refresh_from_db()
        assert obj.import_status == "pending"
        m.assert_any_call(tasks.import_track_file.delay, track_file_id=obj.pk)

    finished.refresh_from_db()
    assert finished.import_status == "finished"
    assert m.call_count == 3
