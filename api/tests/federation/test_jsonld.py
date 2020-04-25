import pytest

from rest_framework import serializers

from funkwhale_api.federation import contexts
from funkwhale_api.federation import jsonld


def test_expand_no_external_request():
    payload = {
        "id": "https://noop/federation/actors/demo",
        "outbox": "https://noop/federation/actors/demo/outbox",
        "inbox": "https://noop/federation/actors/demo/inbox",
        "preferredUsername": "demo",
        "type": "Person",
        "name": "demo",
        "followers": "https://noop/federation/actors/demo/followers",
        "following": "https://noop/federation/actors/demo/following",
        "manuallyApprovesFollowers": False,
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
            {},
        ],
        "publicKey": {
            "owner": "https://noop/federation/actors/demo",
            "publicKeyPem": "-----BEGIN RSA PUBLIC KEY-----\nMIIBCgKCAQEAxPDd/oXx0ClJ2BuBZ937AiERjvoroEpNebg34Cdl6FYsb2Auib8b\nCQjdjLjK/1ag35lmqmsECqtoDYWOo4tGilZJW47TWmXfcvCMH2Sw9FqdOlzpV1RI\nm8kc0Lu1CC2xOTctqIwSH7kDDnS4+S5hSxRdMTeNQNoirncY1CXa9TmJR1lE2HWz\n+B05ewzMrSen3l3fJLQFoI2GVbbjj+tvILKBL1oG5MtYieYqjt2sqtqy/OpWUAC7\nlRERRzd4t5xPBKykWkBCAOh80pvPue5V4s+xUMr7ioKTcm6pq+pNBta5w0hUYIcT\nMefQOnNuR4J0meIqiDLcrglGAmM6AVFwYwIDAQAB\n-----END RSA PUBLIC KEY-----\n",  # noqa
            "id": "https://noop/federation/actors/demo#main-key",
        },
        "endpoints": {"sharedInbox": "https://noop/federation/shared/inbox"},
    }

    expected = {
        contexts.AS.endpoints: [
            {contexts.AS.sharedInbox: [{"@id": "https://noop/federation/shared/inbox"}]}
        ],
        contexts.AS.followers: [
            {"@id": "https://noop/federation/actors/demo/followers"}
        ],
        contexts.AS.following: [
            {"@id": "https://noop/federation/actors/demo/following"}
        ],
        "@id": "https://noop/federation/actors/demo",
        "http://www.w3.org/ns/ldp#inbox": [
            {"@id": "https://noop/federation/actors/demo/inbox"}
        ],
        contexts.AS.manuallyApprovesFollowers: [{"@value": False}],
        contexts.AS.name: [{"@value": "demo"}],
        contexts.AS.outbox: [{"@id": "https://noop/federation/actors/demo/outbox"}],
        contexts.AS.preferredUsername: [{"@value": "demo"}],
        contexts.SEC.publicKey: [
            {
                "@id": "https://noop/federation/actors/demo#main-key",
                contexts.SEC.owner: [{"@id": "https://noop/federation/actors/demo"}],
                contexts.SEC.publicKeyPem: [
                    {
                        "@value": "-----BEGIN RSA PUBLIC KEY-----\nMIIBCgKCAQEAxPDd/oXx0ClJ2BuBZ937AiERjvoroEpNebg34Cdl6FYsb2Auib8b\nCQjdjLjK/1ag35lmqmsECqtoDYWOo4tGilZJW47TWmXfcvCMH2Sw9FqdOlzpV1RI\nm8kc0Lu1CC2xOTctqIwSH7kDDnS4+S5hSxRdMTeNQNoirncY1CXa9TmJR1lE2HWz\n+B05ewzMrSen3l3fJLQFoI2GVbbjj+tvILKBL1oG5MtYieYqjt2sqtqy/OpWUAC7\nlRERRzd4t5xPBKykWkBCAOh80pvPue5V4s+xUMr7ioKTcm6pq+pNBta5w0hUYIcT\nMefQOnNuR4J0meIqiDLcrglGAmM6AVFwYwIDAQAB\n-----END RSA PUBLIC KEY-----\n"  # noqa
                    }
                ],
            }
        ],
        "@type": [contexts.AS.Person],
    }

    doc = jsonld.expand(payload)

    assert doc == expected


def test_expand_no_external_request_pleroma():
    payload = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://pleroma.example/schemas/litepub-0.1.jsonld",
            {"@language": "und"},
        ],
        "endpoints": {
            "oauthAuthorizationEndpoint": "https://pleroma.example/oauth/authorize",
            "oauthRegistrationEndpoint": "https://pleroma.example/api/v1/apps",
            "oauthTokenEndpoint": "https://pleroma.example/oauth/token",
            "sharedInbox": "https://pleroma.example/inbox",
            "uploadMedia": "https://pleroma.example/api/ap/upload_media",
        },
        "followers": "https://pleroma.example/internal/fetch/followers",
        "following": "https://pleroma.example/internal/fetch/following",
        "id": "https://pleroma.example/internal/fetch",
        "inbox": "https://pleroma.example/internal/fetch/inbox",
        "invisible": True,
        "manuallyApprovesFollowers": False,
        "name": "Pleroma",
        "preferredUsername": "internal.fetch",
        "publicKey": {
            "id": "https://pleroma.example/internal/fetch#main-key",
            "owner": "https://pleroma.example/internal/fetch",
            "publicKeyPem": "PEM",
        },
        "summary": "An internal service actor for this Pleroma instance.  No user-serviceable parts inside.",
        "type": "Application",
        "url": "https://pleroma.example/internal/fetch",
    }

    expected = {
        contexts.AS.endpoints: [
            {
                contexts.AS.sharedInbox: [{"@id": "https://pleroma.example/inbox"}],
                contexts.AS.oauthAuthorizationEndpoint: [
                    {"@id": "https://pleroma.example/oauth/authorize"}
                ],
                contexts.LITEPUB.oauthRegistrationEndpoint: [
                    {"@id": "https://pleroma.example/api/v1/apps"}
                ],
                contexts.AS.oauthTokenEndpoint: [
                    {"@id": "https://pleroma.example/oauth/token"}
                ],
                contexts.AS.uploadMedia: [
                    {"@id": "https://pleroma.example/api/ap/upload_media"}
                ],
            },
        ],
        contexts.AS.followers: [
            {"@id": "https://pleroma.example/internal/fetch/followers"}
        ],
        contexts.AS.following: [
            {"@id": "https://pleroma.example/internal/fetch/following"}
        ],
        "@id": "https://pleroma.example/internal/fetch",
        "http://www.w3.org/ns/ldp#inbox": [
            {"@id": "https://pleroma.example/internal/fetch/inbox"}
        ],
        contexts.LITEPUB.invisible: [{"@value": True}],
        contexts.AS.manuallyApprovesFollowers: [{"@value": False}],
        contexts.AS.name: [{"@language": "und", "@value": "Pleroma"}],
        contexts.AS.summary: [
            {
                "@language": "und",
                "@value": "An internal service actor for this Pleroma instance.  No user-serviceable parts inside.",
            }
        ],
        contexts.AS.url: [{"@id": "https://pleroma.example/internal/fetch"}],
        contexts.AS.preferredUsername: [
            {"@language": "und", "@value": "internal.fetch"}
        ],
        contexts.SEC.publicKey: [
            {
                "@id": "https://pleroma.example/internal/fetch#main-key",
                contexts.SEC.owner: [{"@id": "https://pleroma.example/internal/fetch"}],
                contexts.SEC.publicKeyPem: [{"@language": "und", "@value": "PEM"}],
            }
        ],
        "@type": [contexts.AS.Application],
    }

    doc = jsonld.expand(payload)

    assert doc[contexts.AS.endpoints] == expected[contexts.AS.endpoints]
    assert doc == expected


def test_expand_remote_doc(r_mock):
    url = "https://noop/federation/actors/demo"
    payload = {
        "id": url,
        "outbox": "https://noop/federation/actors/demo/outbox",
        "inbox": "https://noop/federation/actors/demo/inbox",
        "preferredUsername": "demo",
        "type": "Person",
        "name": "demo",
        "followers": "https://noop/federation/actors/demo/followers",
        "following": "https://noop/federation/actors/demo/following",
        "manuallyApprovesFollowers": False,
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
            {},
        ],
        "publicKey": {
            "owner": "https://noop/federation/actors/demo",
            "publicKeyPem": "-----BEGIN RSA PUBLIC KEY-----\nMIIBCgKCAQEAxPDd/oXx0ClJ2BuBZ937AiERjvoroEpNebg34Cdl6FYsb2Auib8b\nCQjdjLjK/1ag35lmqmsECqtoDYWOo4tGilZJW47TWmXfcvCMH2Sw9FqdOlzpV1RI\nm8kc0Lu1CC2xOTctqIwSH7kDDnS4+S5hSxRdMTeNQNoirncY1CXa9TmJR1lE2HWz\n+B05ewzMrSen3l3fJLQFoI2GVbbjj+tvILKBL1oG5MtYieYqjt2sqtqy/OpWUAC7\nlRERRzd4t5xPBKykWkBCAOh80pvPue5V4s+xUMr7ioKTcm6pq+pNBta5w0hUYIcT\nMefQOnNuR4J0meIqiDLcrglGAmM6AVFwYwIDAQAB\n-----END RSA PUBLIC KEY-----\n",  # noqa
            "id": "https://noop/federation/actors/demo#main-key",
        },
        "endpoints": {"sharedInbox": "https://noop/federation/shared/inbox"},
    }
    r_mock.get(url, json=payload)

    expected = {
        contexts.AS.endpoints: [
            {contexts.AS.sharedInbox: [{"@id": "https://noop/federation/shared/inbox"}]}
        ],
        contexts.AS.followers: [
            {"@id": "https://noop/federation/actors/demo/followers"}
        ],
        contexts.AS.following: [
            {"@id": "https://noop/federation/actors/demo/following"}
        ],
        "@id": "https://noop/federation/actors/demo",
        "http://www.w3.org/ns/ldp#inbox": [
            {"@id": "https://noop/federation/actors/demo/inbox"}
        ],
        contexts.AS.manuallyApprovesFollowers: [{"@value": False}],
        contexts.AS.name: [{"@value": "demo"}],
        contexts.AS.outbox: [{"@id": "https://noop/federation/actors/demo/outbox"}],
        contexts.AS.preferredUsername: [{"@value": "demo"}],
        contexts.SEC.publicKey: [
            {
                "@id": "https://noop/federation/actors/demo#main-key",
                contexts.SEC.owner: [{"@id": "https://noop/federation/actors/demo"}],
                contexts.SEC.publicKeyPem: [
                    {
                        "@value": "-----BEGIN RSA PUBLIC KEY-----\nMIIBCgKCAQEAxPDd/oXx0ClJ2BuBZ937AiERjvoroEpNebg34Cdl6FYsb2Auib8b\nCQjdjLjK/1ag35lmqmsECqtoDYWOo4tGilZJW47TWmXfcvCMH2Sw9FqdOlzpV1RI\nm8kc0Lu1CC2xOTctqIwSH7kDDnS4+S5hSxRdMTeNQNoirncY1CXa9TmJR1lE2HWz\n+B05ewzMrSen3l3fJLQFoI2GVbbjj+tvILKBL1oG5MtYieYqjt2sqtqy/OpWUAC7\nlRERRzd4t5xPBKykWkBCAOh80pvPue5V4s+xUMr7ioKTcm6pq+pNBta5w0hUYIcT\nMefQOnNuR4J0meIqiDLcrglGAmM6AVFwYwIDAQAB\n-----END RSA PUBLIC KEY-----\n"  # noqa
                    }
                ],
            }
        ],
        "@type": [contexts.AS.Person],
    }

    doc = jsonld.expand(url)

    assert doc == expected


async def test_fetch_many(a_responses):
    doc = {
        "@context": jsonld.get_default_context(),
        "id": "https://noop/federation/actors/demo",
        "type": "Person",
        "followers": "https://noop/federation/actors/demo/followers",
    }
    followers_doc = {
        "@context": jsonld.get_default_context(),
        "id": "https://noop/federation/actors/demo/followers",
        "type": "Collection",
    }

    a_responses.get(doc["id"], payload=doc)
    a_responses.get(followers_doc["id"], payload=followers_doc)
    fetched = await jsonld.fetch_many(doc["id"], followers_doc["id"])
    assert fetched == {followers_doc["id"]: followers_doc, doc["id"]: doc}


def test_dereference():

    followers_doc = {
        "@context": jsonld.get_default_context(),
        "id": "https://noop/federation/actors/demo/followers",
        "type": "Collection",
    }

    actor_doc = {
        "@context": jsonld.get_default_context(),
        "id": "https://noop/federation/actors/demo",
        "type": "Person",
        "followers": "https://noop/federation/actors/demo/followers",
    }

    store = {followers_doc["id"]: followers_doc, actor_doc["id"]: actor_doc}

    payload = {
        "followers": {"@id": followers_doc["id"]},
        "actor": [
            {"@id": actor_doc["id"], "hello": "world"},
            {"somethingElse": [{"@id": actor_doc["id"]}]},
        ],
    }
    expected = {
        "followers": followers_doc,
        "actor": [actor_doc, {"somethingElse": [actor_doc]}],
    }

    assert jsonld.dereference(payload, store) == expected


def test_prepare_for_serializer():
    config = {
        "followers": {
            "property": contexts.AS.followers,
            "keep": "first",
            "attr": "@id",
        },
        "name": {"property": contexts.AS.name, "keep": "first", "attr": "@value"},
        "keys": {"property": contexts.SEC.publicKey, "type": "raw"},
    }

    payload = {
        "@id": "https://noop/federation/actors/demo",
        "@type": [contexts.AS.Person],
        contexts.AS.followers: [
            {"@id": "https://noop/federation/actors/demo/followers"}
        ],
        contexts.AS.name: [{"@value": "demo"}],
        contexts.SEC.publicKey: [
            {"@id": "https://noop/federation/actors/demo#main-key1"},
            {"@id": "https://noop/federation/actors/demo#main-key2"},
        ],
    }

    expected = {
        "id": "https://noop/federation/actors/demo",
        "type": contexts.AS.Person,
        "followers": "https://noop/federation/actors/demo/followers",
        "name": "demo",
        "keys": [
            {"@id": "https://noop/federation/actors/demo#main-key1"},
            {"@id": "https://noop/federation/actors/demo#main-key2"},
        ],
    }

    assert jsonld.prepare_for_serializer(payload, config) == expected


def test_prepare_for_serializer_fallback():
    config = {
        "name": {"property": contexts.AS.name, "keep": "first", "attr": "@value"},
        "album": {"property": contexts.FW.Album, "keep": "first"},
        "noop_album": {"property": contexts.NOOP.Album, "keep": "first"},
    }
    fallbacks = {"album": ["noop_album"]}

    payload = {
        "@id": "https://noop/federation/actors/demo",
        "@type": [contexts.AS.Person],
        contexts.AS.name: [{"@value": "demo"}],
        contexts.NOOP.Album: [{"@id": "https://noop/federation/album/demo"}],
    }

    expected = {
        "id": "https://noop/federation/actors/demo",
        "type": contexts.AS.Person,
        "name": "demo",
        "album": {"@id": "https://noop/federation/album/demo"},
        "noop_album": {"@id": "https://noop/federation/album/demo"},
    }

    assert (
        jsonld.prepare_for_serializer(payload, config, fallbacks=fallbacks) == expected
    )


def test_jsonld_serializer_fallback():
    class TestSerializer(jsonld.JsonLdSerializer):
        id = serializers.URLField()
        type = serializers.CharField()
        name = serializers.CharField()
        username = serializers.CharField()
        total = serializers.IntegerField()

        class Meta:
            jsonld_fallbacks = {"total": ["total_fallback"]}
            jsonld_mapping = {
                "name": {
                    "property": contexts.AS.name,
                    "keep": "first",
                    "attr": "@value",
                },
                "username": {
                    "property": contexts.AS.preferredUsername,
                    "keep": "first",
                    "attr": "@value",
                },
                "total": {
                    "property": contexts.AS.totalItems,
                    "keep": "first",
                    "attr": "@value",
                },
                "total_fallback": {
                    "property": contexts.NOOP.count,
                    "keep": "first",
                    "attr": "@value",
                },
            }

    payload = {
        "@context": jsonld.get_default_context(),
        "id": "https://noop.url/federation/actors/demo",
        "type": "Person",
        "name": "Hello",
        "preferredUsername": "World",
        "count": 42,
    }

    serializer = TestSerializer(data=payload)
    assert serializer.is_valid(raise_exception=True)

    assert serializer.validated_data == {
        "type": contexts.AS.Person,
        "id": payload["id"],
        "name": payload["name"],
        "username": payload["preferredUsername"],
        "total": 42,
    }


def test_jsonld_serializer_dereference(a_responses):
    class TestSerializer(jsonld.JsonLdSerializer):
        id = serializers.URLField()
        type = serializers.CharField()
        followers = serializers.JSONField()

        class Meta:
            jsonld_mapping = {
                "followers": {"property": contexts.AS.followers, "dereference": True}
            }

    payload = {
        "@context": jsonld.get_default_context(),
        "id": "https://noop.url/federation/actors/demo",
        "type": "Person",
        "followers": "https://noop.url/federation/actors/demo/followers",
    }

    followers_doc = {
        "@context": jsonld.get_default_context(),
        "id": "https://noop.url/federation/actors/demo/followers",
        "type": "Collection",
    }

    a_responses.get(followers_doc["id"], payload=followers_doc)
    serializer = TestSerializer(data=payload)

    assert serializer.is_valid(raise_exception=True)
    assert serializer.validated_data == {
        "type": contexts.AS.Person,
        "id": payload["id"],
        "followers": [followers_doc],
    }


@pytest.mark.parametrize(
    "doc, ctx, expected",
    [
        (
            {"@context": [{}], "hello": "world"},
            "http://test",
            {"@context": [{}, "http://test"], "hello": "world"},
        ),
        (
            {"@context": {"key": "value"}, "hello": "world"},
            "http://test",
            {"@context": [{"key": "value"}, "http://test"], "hello": "world"},
        ),
        (
            {"@context": "http://as", "hello": "world"},
            "http://test",
            {"@context": ["http://as", "http://test"], "hello": "world"},
        ),
    ],
)
def test_insert_context(doc, ctx, expected):
    jsonld.insert_context(ctx, doc)
    assert doc == expected
