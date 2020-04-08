import pytest

from funkwhale_api.federation import routes
from funkwhale_api.federation import serializers


def test_pleroma_actor_from_ap(factories):

    payload = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://test.federation/schemas/litepub-0.1.jsonld",
            {"@language": "und"},
        ],
        "endpoints": {
            "oauthAuthorizationEndpoint": "https://test.federation/oauth/authorize",
            "oauthRegistrationEndpoint": "https://test.federation/api/v1/apps",
            "oauthTokenEndpoint": "https://test.federation/oauth/token",
            "sharedInbox": "https://test.federation/inbox",
            "uploadMedia": "https://test.federation/api/ap/upload_media",
        },
        "followers": "https://test.federation/internal/fetch/followers",
        "following": "https://test.federation/internal/fetch/following",
        "id": "https://test.federation/internal/fetch",
        "inbox": "https://test.federation/internal/fetch/inbox",
        "invisible": True,
        "manuallyApprovesFollowers": False,
        "name": "Pleroma",
        "preferredUsername": "internal.fetch",
        "publicKey": {
            "id": "https://test.federation/internal/fetch#main-key",
            "owner": "https://test.federation/internal/fetch",
            "publicKeyPem": "PEM",
        },
        "summary": "An internal service actor for this Pleroma instance.  No user-serviceable parts inside.",
        "type": "Application",
        "url": "https://test.federation/internal/fetch",
    }

    serializer = serializers.ActorSerializer(data=payload)
    assert serializer.is_valid(raise_exception=True)
    actor = serializer.save()

    assert actor.fid == payload["id"]
    assert actor.url == payload["url"]
    assert actor.inbox_url == payload["inbox"]
    assert actor.shared_inbox_url == payload["endpoints"]["sharedInbox"]
    assert actor.outbox_url is None
    assert actor.following_url == payload["following"]
    assert actor.followers_url == payload["followers"]
    assert actor.followers_url == payload["followers"]
    assert actor.type == payload["type"]
    assert actor.preferred_username == payload["preferredUsername"]
    assert actor.name == payload["name"]
    assert actor.summary_obj.text == payload["summary"]
    assert actor.summary_obj.content_type == "text/html"
    assert actor.fid == payload["url"]
    assert actor.manually_approves_followers is payload["manuallyApprovesFollowers"]
    assert actor.private_key is None
    assert actor.public_key == payload["publicKey"]["publicKeyPem"]
    assert actor.domain_id == "test.federation"


def test_reel2bits_channel_from_actor_ap(db, mocker):
    mocker.patch("funkwhale_api.federation.tasks.update_domain_nodeinfo")
    payload = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
            {
                "Hashtag": "as:Hashtag",
                "PropertyValue": "schema:PropertyValue",
                "artwork": "reel2bits:artwork",
                "featured": "toot:featured",
                "genre": "reel2bits:genre",
                "licence": "reel2bits:licence",
                "manuallyApprovesFollowers": "as:manuallyApprovesFollowers",
                "reel2bits": "http://reel2bits.org/ns#",
                "schema": "http://schema.org#",
                "sensitive": "as:sensitive",
                "tags": "reel2bits:tags",
                "toot": "http://joinmastodon.org/ns#",
                "transcode_url": "reel2bits:transcode_url",
                "transcoded": "reel2bits:transcoded",
                "value": "schema:value",
            },
        ],
        "endpoints": {"sharedInbox": "https://r2b.example/inbox"},
        "followers": "https://r2b.example/user/anna/followers",
        "following": "https://r2b.example/user/anna/followings",
        "icon": {
            "type": "Image",
            "url": "https://r2b.example/uploads/avatars/anna/f4930.jpg",
        },
        "id": "https://r2b.example/user/anna",
        "inbox": "https://r2b.example/user/anna/inbox",
        "manuallyApprovesFollowers": False,
        "name": "Anna",
        "outbox": "https://r2b.example/user/anna/outbox",
        "preferredUsername": "anna",
        "publicKey": {
            "id": "https://r2b.example/user/anna#main-key",
            "owner": "https://r2b.example/user/anna",
            "publicKeyPem": "MIIBIxaeikqh",
        },
        "type": "Person",
        "url": [
            {
                "type": "Link",
                "mediaType": "text/html",
                "href": "https://r2b.example/@anna",
            },
            {
                "type": "Link",
                "mediaType": "application/rss+xml",
                "href": "https://r2b.example/@anna.rss",
            },
        ],
    }

    serializer = serializers.ActorSerializer(data=payload)
    assert serializer.is_valid(raise_exception=True)
    actor = serializer.save()

    assert actor.fid == payload["id"]
    assert actor.url == payload["url"][0]["href"]
    assert actor.inbox_url == payload["inbox"]
    assert actor.shared_inbox_url == payload["endpoints"]["sharedInbox"]
    assert actor.outbox_url is payload["outbox"]
    assert actor.following_url == payload["following"]
    assert actor.followers_url == payload["followers"]
    assert actor.followers_url == payload["followers"]
    assert actor.type == payload["type"]
    assert actor.preferred_username == payload["preferredUsername"]
    assert actor.name == payload["name"]
    assert actor.manually_approves_followers is payload["manuallyApprovesFollowers"]
    assert actor.private_key is None
    assert actor.public_key == payload["publicKey"]["publicKeyPem"]
    assert actor.domain_id == "r2b.example"

    channel = actor.get_channel()

    assert channel.attributed_to == actor
    assert channel.rss_url == payload["url"][1]["href"]
    assert channel.artist.name == actor.name
    assert channel.artist.attributed_to == actor


def test_reel2bits_upload_create(factories):
    channel = factories["audio.Channel"]()
    payload = {
        "id": "https://r2b.example/outbox/cb89c969224d7c9d",
        "to": ["https://www.w3.org/ns/activitystreams#Public"],
        "type": "Create",
        "actor": "https://r2b.example/user/anna",
        "object": {
            "cc": ["https://r2b.example/user/anna/followers"],
            "id": "https://r2b.example/outbox/cb89c969224d7c9d/activity",
            "to": ["https://www.w3.org/ns/activitystreams#Public"],
            "url": {
                "href": "https://r2b.example/uploads/sounds/anna/test.mp3",
                "type": "Link",
                "mediaType": "audio/mpeg",
            },
            "name": "nya",
            "tag": [
                {"name": "#nya", "type": "Hashtag"},
                {"name": "#cat", "type": "Hashtag"},
                {"name": "#paws", "type": "Hashtag"},
            ],
            "type": "Audio",
            "genre": "cat",
            "image": {
                "url": "https://r2b.example/uploads/artwork_sounds/anna/test.jpg",
                "type": "Image",
                "mediaType": "image/jpeg",
            },
            "content": "nya nya",
            "licence": {"id": "0", "icon": "", "link": "", "name": "Not Specified"},
            "mediaType": "text/plain",
            "published": "2020-04-08T12:47:29Z",
            "attributedTo": "https://r2b.example/user/anna",
        },
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
            {
                "toot": "http://joinmastodon.org/ns#",
                "Hashtag": "as:Hashtag",
                "featured": "toot:featured",
                "sensitive": "as:sensitive",
            },
        ],
        "published": "2020-04-08T12:47:29Z",
    }
    serializer = serializers.ChannelCreateUploadSerializer(
        data=payload, context={"channel": channel}
    )
    assert serializer.is_valid(raise_exception=True) is True

    serializer.save()


def test_reel2bits_upload_delete(factories):
    actor = factories["federation.Actor"]()
    channel = factories["audio.Channel"](actor=actor, attributed_to=actor)
    upload = factories["music.Upload"](channel=channel, track__attributed_to=actor)
    payload = {
        "id": "https://r2b.example/outbox/4987acc5b25f0aac",
        "to": [
            "https://channels.tests.funkwhale.audio/federation/actors/demo",
            "https://www.w3.org/ns/activitystreams#Public",
        ],
        "type": "Delete",
        "actor": actor.fid,
        "object": {"id": upload.fid, "type": "Tombstone"},
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
            {
                "toot": "http://joinmastodon.org/ns#",
                "Hashtag": "as:Hashtag",
                "featured": "toot:featured",
                "sensitive": "as:sensitive",
            },
        ],
    }

    routes.inbox_delete(
        payload, context={"actor": actor, "raise_exception": True, "activity": payload},
    )

    with pytest.raises(upload.track.DoesNotExist):
        upload.track.refresh_from_db()
    with pytest.raises(upload.DoesNotExist):
        upload.refresh_from_db()
