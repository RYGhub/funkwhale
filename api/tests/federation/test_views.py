import pytest
from django.core.paginator import Paginator
from django.urls import reverse

from funkwhale_api.federation import actors, serializers, webfinger


@pytest.mark.parametrize("system_actor", actors.SYSTEM_ACTORS.keys())
def test_instance_actors(system_actor, db, api_client):
    actor = actors.SYSTEM_ACTORS[system_actor].get_actor_instance()
    url = reverse("federation:instance-actors-detail", kwargs={"actor": system_actor})
    response = api_client.get(url)
    serializer = serializers.ActorSerializer(actor)

    if system_actor == "library":
        response.data.pop("url")
    assert response.status_code == 200
    assert response.data == serializer.data


def test_wellknown_webfinger_validates_resource(db, api_client, settings, mocker):
    clean = mocker.spy(webfinger, "clean_resource")
    url = reverse("federation:well-known-webfinger")
    response = api_client.get(url, data={"resource": "something"})

    clean.assert_called_once_with("something")
    assert url == "/.well-known/webfinger"
    assert response.status_code == 400
    assert response.data["errors"]["resource"] == ("Missing webfinger resource type")


@pytest.mark.parametrize("system_actor", actors.SYSTEM_ACTORS.keys())
def test_wellknown_webfinger_system(system_actor, db, api_client, settings, mocker):
    actor = actors.SYSTEM_ACTORS[system_actor].get_actor_instance()
    url = reverse("federation:well-known-webfinger")
    response = api_client.get(
        url,
        data={"resource": "acct:{}".format(actor.webfinger_subject)},
        HTTP_ACCEPT="application/jrd+json",
    )
    serializer = serializers.ActorWebfingerSerializer(actor)

    assert response.status_code == 200
    assert response["Content-Type"] == "application/jrd+json"
    assert response.data == serializer.data


def test_wellknown_nodeinfo(db, preferences, api_client, settings):
    expected = {
        "links": [
            {
                "rel": "http://nodeinfo.diaspora.software/ns/schema/2.0",
                "href": "{}{}".format(
                    settings.FUNKWHALE_URL, reverse("api:v1:instance:nodeinfo-2.0")
                ),
            }
        ]
    }
    url = reverse("federation:well-known-nodeinfo")
    response = api_client.get(url, HTTP_ACCEPT="application/jrd+json")
    assert response.status_code == 200
    assert response["Content-Type"] == "application/jrd+json"
    assert response.data == expected


def test_wellknown_nodeinfo_disabled(db, preferences, api_client):
    preferences["instance__nodeinfo_enabled"] = False
    url = reverse("federation:well-known-nodeinfo")
    response = api_client.get(url)
    assert response.status_code == 404


def test_local_actor_detail(factories, api_client):
    user = factories["users.User"](with_actor=True)
    url = reverse(
        "federation:actors-detail",
        kwargs={"preferred_username": user.actor.preferred_username},
    )
    serializer = serializers.ActorSerializer(user.actor)
    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data == serializer.data


def test_local_actor_inbox_post_requires_auth(factories, api_client):
    user = factories["users.User"](with_actor=True)
    url = reverse(
        "federation:actors-inbox",
        kwargs={"preferred_username": user.actor.preferred_username},
    )
    response = api_client.post(url, {"hello": "world"})

    assert response.status_code == 403


def test_local_actor_inbox_post(factories, api_client, mocker, authenticated_actor):
    patched_receive = mocker.patch("funkwhale_api.federation.activity.receive")
    user = factories["users.User"](with_actor=True)
    url = reverse(
        "federation:actors-inbox",
        kwargs={"preferred_username": user.actor.preferred_username},
    )
    response = api_client.post(url, {"hello": "world"}, format="json")

    assert response.status_code == 200
    patched_receive.assert_called_once_with(
        activity={"hello": "world"},
        on_behalf_of=authenticated_actor,
        recipient=user.actor,
    )


def test_wellknown_webfinger_local(factories, api_client, settings, mocker):
    user = factories["users.User"](with_actor=True)
    url = reverse("federation:well-known-webfinger")
    response = api_client.get(
        url,
        data={"resource": "acct:{}".format(user.actor.webfinger_subject)},
        HTTP_ACCEPT="application/jrd+json",
    )
    serializer = serializers.ActorWebfingerSerializer(user.actor)

    assert response.status_code == 200
    assert response["Content-Type"] == "application/jrd+json"
    assert response.data == serializer.data


@pytest.mark.parametrize("privacy_level", ["me", "instance", "everyone"])
def test_music_library_retrieve(factories, api_client, privacy_level):
    library = factories["music.Library"](privacy_level=privacy_level)
    expected = serializers.LibrarySerializer(library).data

    url = reverse("federation:music:libraries-detail", kwargs={"uuid": library.uuid})
    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data == expected


def test_music_library_retrieve_page_public(factories, api_client):
    library = factories["music.Library"](privacy_level="everyone")
    tf = factories["music.TrackFile"](library=library)
    id = library.get_federation_id()
    expected = serializers.CollectionPageSerializer(
        {
            "id": id,
            "item_serializer": serializers.AudioSerializer,
            "actor": library.actor,
            "page": Paginator([tf], 1).page(1),
            "name": library.name,
            "summary": library.description,
        }
    ).data

    url = reverse("federation:music:libraries-detail", kwargs={"uuid": library.uuid})
    response = api_client.get(url, {"page": 1})

    assert response.status_code == 200
    assert response.data == expected


@pytest.mark.parametrize("privacy_level", ["me", "instance"])
def test_music_library_retrieve_page_private(factories, api_client, privacy_level):
    library = factories["music.Library"](privacy_level=privacy_level)
    url = reverse("federation:music:libraries-detail", kwargs={"uuid": library.uuid})
    response = api_client.get(url, {"page": 1})

    assert response.status_code == 403


@pytest.mark.parametrize("approved,expected", [(True, 200), (False, 403)])
def test_music_library_retrieve_page_follow(
    factories, api_client, authenticated_actor, approved, expected
):
    library = factories["music.Library"](privacy_level="me")
    factories["federation.LibraryFollow"](
        actor=authenticated_actor, target=library, approved=approved
    )
    url = reverse("federation:music:libraries-detail", kwargs={"uuid": library.uuid})
    response = api_client.get(url, {"page": 1})

    assert response.status_code == expected
