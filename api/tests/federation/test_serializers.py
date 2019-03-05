from funkwhale_api.federation import keys
from funkwhale_api.federation import jsonld
from funkwhale_api.federation import serializers


def test_actor_serializer_from_ap(db):
    private, public = keys.get_key_pair()
    actor_url = "https://test.federation/actor"
    payload = {
        "@context": jsonld.get_default_context(),
        "id": actor_url,
        "type": "Person",
        "outbox": "https://test.com/outbox",
        "inbox": "https://test.com/inbox",
        "following": "https://test.com/following",
        "followers": "https://test.com/followers",
        "preferredUsername": "test",
        "name": "Test",
        "summary": "Hello world",
        "manuallyApprovesFollowers": True,
        "publicKey": {
            "publicKeyPem": public.decode("utf-8"),
            "owner": actor_url,
            "id": actor_url + "#main-key",
        },
        "endpoints": {"sharedInbox": "https://noop.url/federation/shared/inbox"},
    }

    serializer = serializers.ActorSerializer(data=payload)
    assert serializer.is_valid(raise_exception=True)
    actor = serializer.save()

    assert actor.fid == actor_url
    assert actor.url is None
    assert actor.inbox_url == payload["inbox"]
    assert actor.shared_inbox_url == payload["endpoints"]["sharedInbox"]
    assert actor.outbox_url == payload["outbox"]
    assert actor.following_url == payload["following"]
    assert actor.followers_url == payload["followers"]
    assert actor.followers_url == payload["followers"]
    assert actor.type == "Person"
    assert actor.preferred_username == payload["preferredUsername"]
    assert actor.name == payload["name"]
    assert actor.summary == payload["summary"]
    assert actor.fid == actor_url
    assert actor.manually_approves_followers is True
    assert actor.private_key is None
    assert actor.public_key == payload["publicKey"]["publicKeyPem"]
    assert actor.domain_id == "test.federation"
