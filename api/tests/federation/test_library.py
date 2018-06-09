from funkwhale_api.federation import library
from funkwhale_api.federation import serializers


def test_library_scan_from_account_name(mocker, factories):
    actor = factories["federation.Actor"](
        preferred_username="library", domain="test.library"
    )
    get_resource_result = {"actor_url": actor.url}
    get_resource = mocker.patch(
        "funkwhale_api.federation.webfinger.get_resource",
        return_value=get_resource_result,
    )

    actor_data = serializers.ActorSerializer(actor).data
    actor_data["manuallyApprovesFollowers"] = False
    actor_data["url"] = [
        {
            "type": "Link",
            "name": "library",
            "mediaType": "application/activity+json",
            "href": "https://test.library",
        }
    ]
    get_actor_data = mocker.patch(
        "funkwhale_api.federation.actors.get_actor_data", return_value=actor_data
    )

    get_library_data_result = {"test": "test"}
    get_library_data = mocker.patch(
        "funkwhale_api.federation.library.get_library_data",
        return_value=get_library_data_result,
    )

    result = library.scan_from_account_name("library@test.actor")

    get_resource.assert_called_once_with("acct:library@test.actor")
    get_actor_data.assert_called_once_with(actor.url)
    get_library_data.assert_called_once_with(actor_data["url"][0]["href"])

    assert result == {
        "webfinger": get_resource_result,
        "actor": actor_data,
        "library": get_library_data_result,
        "local": {"following": False, "awaiting_approval": False},
    }


def test_get_library_data(r_mock, factories):
    actor = factories["federation.Actor"]()
    url = "https://test.library"
    conf = {"id": url, "items": [], "actor": actor, "page_size": 5}
    data = serializers.PaginatedCollectionSerializer(conf).data
    r_mock.get(url, json=data)

    result = library.get_library_data(url)
    for f in ["totalItems", "actor", "id", "type"]:
        assert result[f] == data[f]


def test_get_library_data_requires_authentication(r_mock, factories):
    url = "https://test.library"
    r_mock.get(url, status_code=403)
    result = library.get_library_data(url)
    assert result["errors"] == ["Permission denied while scanning library"]
