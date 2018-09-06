import pytest
from django.core.paginator import Paginator

from funkwhale_api.federation import activity, models, serializers, utils


def test_actor_serializer_from_ap(db):
    payload = {
        "id": "https://test.federation/user",
        "type": "Person",
        "following": "https://test.federation/user/following",
        "followers": "https://test.federation/user/followers",
        "inbox": "https://test.federation/user/inbox",
        "outbox": "https://test.federation/user/outbox",
        "preferredUsername": "user",
        "name": "Real User",
        "summary": "Hello world",
        "url": "https://test.federation/@user",
        "manuallyApprovesFollowers": False,
        "publicKey": {
            "id": "https://test.federation/user#main-key",
            "owner": "https://test.federation/user",
            "publicKeyPem": "yolo",
        },
        "endpoints": {"sharedInbox": "https://test.federation/inbox"},
    }

    serializer = serializers.ActorSerializer(data=payload)
    assert serializer.is_valid(raise_exception=True)

    actor = serializer.build()

    assert actor.fid == payload["id"]
    assert actor.inbox_url == payload["inbox"]
    assert actor.outbox_url == payload["outbox"]
    assert actor.shared_inbox_url == payload["endpoints"]["sharedInbox"]
    assert actor.followers_url == payload["followers"]
    assert actor.following_url == payload["following"]
    assert actor.public_key == payload["publicKey"]["publicKeyPem"]
    assert actor.preferred_username == payload["preferredUsername"]
    assert actor.name == payload["name"]
    assert actor.domain == "test.federation"
    assert actor.summary == payload["summary"]
    assert actor.type == "Person"
    assert actor.manually_approves_followers == payload["manuallyApprovesFollowers"]


def test_actor_serializer_only_mandatory_field_from_ap(db):
    payload = {
        "id": "https://test.federation/user",
        "type": "Person",
        "following": "https://test.federation/user/following",
        "followers": "https://test.federation/user/followers",
        "inbox": "https://test.federation/user/inbox",
        "outbox": "https://test.federation/user/outbox",
        "preferredUsername": "user",
    }

    serializer = serializers.ActorSerializer(data=payload)
    assert serializer.is_valid(raise_exception=True)

    actor = serializer.build()

    assert actor.fid == payload["id"]
    assert actor.inbox_url == payload["inbox"]
    assert actor.outbox_url == payload["outbox"]
    assert actor.followers_url == payload["followers"]
    assert actor.following_url == payload["following"]
    assert actor.preferred_username == payload["preferredUsername"]
    assert actor.domain == "test.federation"
    assert actor.type == "Person"
    assert actor.manually_approves_followers is None


def test_actor_serializer_to_ap():
    expected = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
            {},
        ],
        "id": "https://test.federation/user",
        "type": "Person",
        "following": "https://test.federation/user/following",
        "followers": "https://test.federation/user/followers",
        "inbox": "https://test.federation/user/inbox",
        "outbox": "https://test.federation/user/outbox",
        "preferredUsername": "user",
        "name": "Real User",
        "summary": "Hello world",
        "manuallyApprovesFollowers": False,
        "publicKey": {
            "id": "https://test.federation/user#main-key",
            "owner": "https://test.federation/user",
            "publicKeyPem": "yolo",
        },
        "endpoints": {"sharedInbox": "https://test.federation/inbox"},
    }
    ac = models.Actor(
        fid=expected["id"],
        inbox_url=expected["inbox"],
        outbox_url=expected["outbox"],
        shared_inbox_url=expected["endpoints"]["sharedInbox"],
        followers_url=expected["followers"],
        following_url=expected["following"],
        public_key=expected["publicKey"]["publicKeyPem"],
        preferred_username=expected["preferredUsername"],
        name=expected["name"],
        domain="test.federation",
        summary=expected["summary"],
        type="Person",
        manually_approves_followers=False,
    )
    serializer = serializers.ActorSerializer(ac)

    assert serializer.data == expected


def test_webfinger_serializer():
    expected = {
        "subject": "acct:service@test.federation",
        "links": [
            {
                "rel": "self",
                "href": "https://test.federation/federation/instance/actor",
                "type": "application/activity+json",
            }
        ],
        "aliases": ["https://test.federation/federation/instance/actor"],
    }
    actor = models.Actor(
        fid=expected["links"][0]["href"],
        preferred_username="service",
        domain="test.federation",
    )
    serializer = serializers.ActorWebfingerSerializer(actor)

    assert serializer.data == expected


def test_follow_serializer_to_ap(factories):
    follow = factories["federation.Follow"](local=True)
    serializer = serializers.FollowSerializer(follow)

    expected = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
            {},
        ],
        "id": follow.get_federation_id(),
        "type": "Follow",
        "actor": follow.actor.fid,
        "object": follow.target.fid,
    }

    assert serializer.data == expected


def test_follow_serializer_save(factories):
    actor = factories["federation.Actor"]()
    target = factories["federation.Actor"]()

    data = {
        "id": "https://test.follow",
        "type": "Follow",
        "actor": actor.fid,
        "object": target.fid,
    }
    serializer = serializers.FollowSerializer(data=data)

    assert serializer.is_valid(raise_exception=True)

    follow = serializer.save()

    assert follow.pk is not None
    assert follow.actor == actor
    assert follow.target == target
    assert follow.approved is None


def test_follow_serializer_save_validates_on_context(factories):
    actor = factories["federation.Actor"]()
    target = factories["federation.Actor"]()
    impostor = factories["federation.Actor"]()

    data = {
        "id": "https://test.follow",
        "type": "Follow",
        "actor": actor.fid,
        "object": target.fid,
    }
    serializer = serializers.FollowSerializer(
        data=data, context={"follow_actor": impostor, "follow_target": impostor}
    )

    assert serializer.is_valid() is False

    assert "actor" in serializer.errors
    assert "object" in serializer.errors


def test_accept_follow_serializer_representation(factories):
    follow = factories["federation.Follow"](approved=None)

    expected = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
            {},
        ],
        "id": follow.get_federation_id() + "/accept",
        "type": "Accept",
        "actor": follow.target.fid,
        "object": serializers.FollowSerializer(follow).data,
    }

    serializer = serializers.AcceptFollowSerializer(follow)

    assert serializer.data == expected


def test_accept_follow_serializer_save(factories):
    follow = factories["federation.Follow"](approved=None)

    data = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
            {},
        ],
        "id": follow.get_federation_id() + "/accept",
        "type": "Accept",
        "actor": follow.target.fid,
        "object": serializers.FollowSerializer(follow).data,
    }

    serializer = serializers.AcceptFollowSerializer(data=data)
    assert serializer.is_valid(raise_exception=True)
    serializer.save()

    follow.refresh_from_db()

    assert follow.approved is True


def test_accept_follow_serializer_validates_on_context(factories):
    follow = factories["federation.Follow"](approved=None)
    impostor = factories["federation.Actor"]()
    data = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
            {},
        ],
        "id": follow.get_federation_id() + "/accept",
        "type": "Accept",
        "actor": impostor.url,
        "object": serializers.FollowSerializer(follow).data,
    }

    serializer = serializers.AcceptFollowSerializer(
        data=data, context={"follow_actor": impostor, "follow_target": impostor}
    )

    assert serializer.is_valid() is False
    assert "actor" in serializer.errors["object"]
    assert "object" in serializer.errors["object"]


def test_undo_follow_serializer_representation(factories):
    follow = factories["federation.Follow"](approved=True)

    expected = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
            {},
        ],
        "id": follow.get_federation_id() + "/undo",
        "type": "Undo",
        "actor": follow.actor.fid,
        "object": serializers.FollowSerializer(follow).data,
    }

    serializer = serializers.UndoFollowSerializer(follow)

    assert serializer.data == expected


def test_undo_follow_serializer_save(factories):
    follow = factories["federation.Follow"](approved=True)

    data = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
            {},
        ],
        "id": follow.get_federation_id() + "/undo",
        "type": "Undo",
        "actor": follow.actor.fid,
        "object": serializers.FollowSerializer(follow).data,
    }

    serializer = serializers.UndoFollowSerializer(data=data)
    assert serializer.is_valid(raise_exception=True)
    serializer.save()

    with pytest.raises(models.Follow.DoesNotExist):
        follow.refresh_from_db()


def test_undo_follow_serializer_validates_on_context(factories):
    follow = factories["federation.Follow"](approved=True)
    impostor = factories["federation.Actor"]()
    data = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
            {},
        ],
        "id": follow.get_federation_id() + "/undo",
        "type": "Undo",
        "actor": impostor.url,
        "object": serializers.FollowSerializer(follow).data,
    }

    serializer = serializers.UndoFollowSerializer(
        data=data, context={"follow_actor": impostor, "follow_target": impostor}
    )

    assert serializer.is_valid() is False
    assert "actor" in serializer.errors["object"]
    assert "object" in serializer.errors["object"]


def test_paginated_collection_serializer(factories):
    tfs = factories["music.TrackFile"].create_batch(size=5)
    actor = factories["federation.Actor"](local=True)

    conf = {
        "id": "https://test.federation/test",
        "items": tfs,
        "item_serializer": serializers.AudioSerializer,
        "actor": actor,
        "page_size": 2,
    }
    expected = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
            {},
        ],
        "type": "Collection",
        "id": conf["id"],
        "actor": actor.fid,
        "totalItems": len(tfs),
        "current": conf["id"] + "?page=1",
        "last": conf["id"] + "?page=3",
        "first": conf["id"] + "?page=1",
    }

    serializer = serializers.PaginatedCollectionSerializer(conf)

    assert serializer.data == expected


def test_paginated_collection_serializer_validation():
    data = {
        "type": "Collection",
        "id": "https://test.federation/test",
        "totalItems": 5,
        "actor": "http://test.actor",
        "first": "https://test.federation/test?page=1",
        "last": "https://test.federation/test?page=1",
        "items": [],
    }

    serializer = serializers.PaginatedCollectionSerializer(data=data)

    assert serializer.is_valid(raise_exception=True) is True
    assert serializer.validated_data["totalItems"] == 5
    assert serializer.validated_data["id"] == data["id"]
    assert serializer.validated_data["actor"] == data["actor"]


def test_collection_page_serializer_validation():
    base = "https://test.federation/test"
    data = {
        "type": "CollectionPage",
        "id": base + "?page=2",
        "totalItems": 5,
        "actor": "https://test.actor",
        "items": [],
        "first": "https://test.federation/test?page=1",
        "last": "https://test.federation/test?page=3",
        "prev": base + "?page=1",
        "next": base + "?page=3",
        "partOf": base,
    }

    serializer = serializers.CollectionPageSerializer(data=data)

    assert serializer.is_valid(raise_exception=True) is True
    assert serializer.validated_data["totalItems"] == 5
    assert serializer.validated_data["id"] == data["id"]
    assert serializer.validated_data["actor"] == data["actor"]
    assert serializer.validated_data["items"] == []
    assert serializer.validated_data["prev"] == data["prev"]
    assert serializer.validated_data["next"] == data["next"]
    assert serializer.validated_data["partOf"] == data["partOf"]


def test_collection_page_serializer_can_validate_child():
    data = {
        "type": "CollectionPage",
        "id": "https://test.page?page=2",
        "actor": "https://test.actor",
        "first": "https://test.page?page=1",
        "last": "https://test.page?page=3",
        "partOf": "https://test.page",
        "totalItems": 1,
        "items": [{"in": "valid"}],
    }

    serializer = serializers.CollectionPageSerializer(
        data=data, context={"item_serializer": serializers.AudioSerializer}
    )

    # child are validated but not included in data if not valid
    assert serializer.is_valid(raise_exception=True) is True
    assert len(serializer.validated_data["items"]) == 0


def test_collection_page_serializer(factories):
    tfs = factories["music.TrackFile"].create_batch(size=5)
    actor = factories["federation.Actor"](local=True)

    conf = {
        "id": "https://test.federation/test",
        "item_serializer": serializers.AudioSerializer,
        "actor": actor,
        "page": Paginator(tfs, 2).page(2),
    }
    expected = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
            {},
        ],
        "type": "CollectionPage",
        "id": conf["id"] + "?page=2",
        "actor": actor.fid,
        "totalItems": len(tfs),
        "partOf": conf["id"],
        "prev": conf["id"] + "?page=1",
        "next": conf["id"] + "?page=3",
        "first": conf["id"] + "?page=1",
        "last": conf["id"] + "?page=3",
        "items": [
            conf["item_serializer"](
                i, context={"actor": actor, "include_ap_context": False}
            ).data
            for i in conf["page"].object_list
        ],
    }

    serializer = serializers.CollectionPageSerializer(conf)

    assert serializer.data == expected


def test_activity_pub_audio_serializer_to_library_track_no_duplicate(factories):
    remote_library = factories["music.Library"]()
    tf = factories["music.TrackFile"].build(library=remote_library)
    data = serializers.AudioSerializer(tf).data
    serializer1 = serializers.AudioSerializer(data=data)
    serializer2 = serializers.AudioSerializer(data=data)

    assert serializer1.is_valid(raise_exception=True) is True
    assert serializer2.is_valid(raise_exception=True) is True

    tf1 = serializer1.save()
    tf2 = serializer2.save()

    assert tf1 == tf2

    assert tf1.library == remote_library
    assert tf1.source == utils.full_url(tf.listen_url)
    assert tf1.mimetype == tf.mimetype
    assert tf1.bitrate == tf.bitrate
    assert tf1.duration == tf.duration
    assert tf1.size == tf.size
    assert tf1.metadata == data
    assert tf1.fid == tf.get_federation_id()
    assert not tf1.audio_file


def test_music_library_serializer_to_ap(factories):
    library = factories["music.Library"]()
    # pending, errored and skippednot included
    factories["music.TrackFile"](import_status="pending")
    factories["music.TrackFile"](import_status="errored")
    factories["music.TrackFile"](import_status="finished")
    serializer = serializers.LibrarySerializer(library)
    expected = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
            {},
        ],
        "type": "Library",
        "id": library.fid,
        "name": library.name,
        "summary": library.description,
        "audience": "",
        "actor": library.actor.fid,
        "totalItems": 0,
        "current": library.fid + "?page=1",
        "last": library.fid + "?page=1",
        "first": library.fid + "?page=1",
    }

    assert serializer.data == expected


def test_music_library_serializer_from_public(factories, mocker):
    actor = factories["federation.Actor"]()
    retrieve = mocker.patch(
        "funkwhale_api.federation.utils.retrieve", return_value=actor
    )
    data = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
            {},
        ],
        "audience": "https://www.w3.org/ns/activitystreams#Public",
        "name": "Hello",
        "summary": "World",
        "type": "Library",
        "id": "https://library.id",
        "actor": actor.fid,
        "totalItems": 12,
        "first": "https://library.id?page=1",
        "last": "https://library.id?page=2",
    }
    serializer = serializers.LibrarySerializer(data=data)

    assert serializer.is_valid(raise_exception=True)

    library = serializer.save()

    assert library.actor == actor
    assert library.fid == data["id"]
    assert library.files_count == data["totalItems"]
    assert library.privacy_level == "everyone"
    assert library.name == "Hello"
    assert library.description == "World"
    retrieve.assert_called_once_with(
        actor.fid,
        queryset=actor.__class__,
        serializer_class=serializers.ActorSerializer,
    )


def test_music_library_serializer_from_private(factories, mocker):
    actor = factories["federation.Actor"]()
    retrieve = mocker.patch(
        "funkwhale_api.federation.utils.retrieve", return_value=actor
    )
    data = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
            {},
        ],
        "audience": "",
        "name": "Hello",
        "summary": "World",
        "type": "Library",
        "id": "https://library.id",
        "actor": actor.fid,
        "totalItems": 12,
        "first": "https://library.id?page=1",
        "last": "https://library.id?page=2",
    }
    serializer = serializers.LibrarySerializer(data=data)

    assert serializer.is_valid(raise_exception=True)

    library = serializer.save()

    assert library.actor == actor
    assert library.fid == data["id"]
    assert library.files_count == data["totalItems"]
    assert library.privacy_level == "me"
    assert library.name == "Hello"
    assert library.description == "World"
    retrieve.assert_called_once_with(
        actor.fid,
        queryset=actor.__class__,
        serializer_class=serializers.ActorSerializer,
    )


def test_activity_pub_audio_serializer_to_ap(factories):
    tf = factories["music.TrackFile"](
        mimetype="audio/mp3", bitrate=42, duration=43, size=44
    )
    expected = {
        "@context": serializers.AP_CONTEXT,
        "type": "Audio",
        "id": tf.get_federation_id(),
        "name": tf.track.full_name,
        "published": tf.creation_date.isoformat(),
        "updated": tf.modification_date.isoformat(),
        "metadata": {
            "artist": {
                "musicbrainz_id": tf.track.artist.mbid,
                "name": tf.track.artist.name,
            },
            "release": {
                "musicbrainz_id": tf.track.album.mbid,
                "title": tf.track.album.title,
            },
            "recording": {"musicbrainz_id": tf.track.mbid, "title": tf.track.title},
            "size": tf.size,
            "length": tf.duration,
            "bitrate": tf.bitrate,
        },
        "url": {
            "href": utils.full_url(tf.listen_url),
            "type": "Link",
            "mediaType": "audio/mp3",
        },
        "library": tf.library.get_federation_id(),
    }

    serializer = serializers.AudioSerializer(tf)

    assert serializer.data == expected


def test_activity_pub_audio_serializer_to_ap_no_mbid(factories):
    tf = factories["music.TrackFile"](
        mimetype="audio/mp3",
        track__mbid=None,
        track__album__mbid=None,
        track__album__artist__mbid=None,
    )
    expected = {
        "@context": serializers.AP_CONTEXT,
        "type": "Audio",
        "id": tf.get_federation_id(),
        "name": tf.track.full_name,
        "published": tf.creation_date.isoformat(),
        "updated": tf.modification_date.isoformat(),
        "metadata": {
            "artist": {"name": tf.track.artist.name, "musicbrainz_id": None},
            "release": {"title": tf.track.album.title, "musicbrainz_id": None},
            "recording": {"title": tf.track.title, "musicbrainz_id": None},
            "size": tf.size,
            "length": None,
            "bitrate": None,
        },
        "url": {
            "href": utils.full_url(tf.listen_url),
            "type": "Link",
            "mediaType": "audio/mp3",
        },
        "library": tf.library.fid,
    }

    serializer = serializers.AudioSerializer(tf)

    assert serializer.data == expected


def test_local_actor_serializer_to_ap(factories):
    expected = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
            {},
        ],
        "id": "https://test.federation/user",
        "type": "Person",
        "following": "https://test.federation/user/following",
        "followers": "https://test.federation/user/followers",
        "inbox": "https://test.federation/user/inbox",
        "outbox": "https://test.federation/user/outbox",
        "preferredUsername": "user",
        "name": "Real User",
        "summary": "Hello world",
        "manuallyApprovesFollowers": False,
        "publicKey": {
            "id": "https://test.federation/user#main-key",
            "owner": "https://test.federation/user",
            "publicKeyPem": "yolo",
        },
        "endpoints": {"sharedInbox": "https://test.federation/inbox"},
    }
    ac = models.Actor.objects.create(
        fid=expected["id"],
        inbox_url=expected["inbox"],
        outbox_url=expected["outbox"],
        shared_inbox_url=expected["endpoints"]["sharedInbox"],
        followers_url=expected["followers"],
        following_url=expected["following"],
        public_key=expected["publicKey"]["publicKeyPem"],
        preferred_username=expected["preferredUsername"],
        name=expected["name"],
        domain="test.federation",
        summary=expected["summary"],
        type="Person",
        manually_approves_followers=False,
    )
    user = factories["users.User"]()
    user.actor = ac
    user.save()
    ac.refresh_from_db()
    expected["icon"] = {
        "type": "Image",
        "mediaType": "image/jpeg",
        "url": utils.full_url(user.avatar.crop["400x400"].url),
    }
    serializer = serializers.ActorSerializer(ac)

    assert serializer.data == expected


def test_activity_serializer_clean_recipients_empty(db):
    s = serializers.BaseActivitySerializer()

    with pytest.raises(serializers.serializers.ValidationError):
        s.validate_recipients({})

    with pytest.raises(serializers.serializers.ValidationError):
        s.validate_recipients({"to": []})

    with pytest.raises(serializers.serializers.ValidationError):
        s.validate_recipients({"cc": []})

    with pytest.raises(serializers.serializers.ValidationError):
        s.validate_recipients({"to": ["nope"]})

    with pytest.raises(serializers.serializers.ValidationError):
        s.validate_recipients({"cc": ["nope"]})


def test_activity_serializer_clean_recipients(factories):
    r1, r2, r3 = factories["federation.Actor"].create_batch(size=3)

    s = serializers.BaseActivitySerializer()

    expected = {"to": [r1, r2], "cc": [r3, activity.PUBLIC_ADDRESS]}

    assert (
        s.validate_recipients(
            {"to": [r1.fid, r2.fid], "cc": [r3.fid, activity.PUBLIC_ADDRESS]}
        )
        == expected
    )


def test_activity_serializer_clean_recipients_local(factories):
    r = factories["federation.Actor"]()

    s = serializers.BaseActivitySerializer(context={"local_recipients": True})
    with pytest.raises(serializers.serializers.ValidationError):
        s.validate_recipients({"to": [r]})
