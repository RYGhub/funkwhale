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
