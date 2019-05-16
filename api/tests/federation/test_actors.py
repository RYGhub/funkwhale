from funkwhale_api.federation import actors, serializers


def test_actor_fetching(r_mock):
    payload = {
        "id": "https://actor.mock/users/actor#main-key",
        "owner": "test",
        "publicKeyPem": "test_pem",
    }
    actor_url = "https://actor.mock/"
    r_mock.get(actor_url, json=payload)
    r = actors.get_actor_data(actor_url)

    assert r == payload


def test_get_actor(factories, r_mock, mocker):
    update_domain_nodeinfo = mocker.patch(
        "funkwhale_api.federation.tasks.update_domain_nodeinfo"
    )
    actor = factories["federation.Actor"].build()
    payload = serializers.ActorSerializer(actor).data
    r_mock.get(actor.fid, json=payload)
    new_actor = actors.get_actor(actor.fid)

    assert new_actor.pk is not None
    assert serializers.ActorSerializer(new_actor).data == payload
    update_domain_nodeinfo.assert_called_once_with(domain_name=new_actor.domain_id)


def test_get_actor_use_existing(factories, preferences, mocker):
    preferences["federation__actor_fetch_delay"] = 60
    actor = factories["federation.Actor"]()
    get_data = mocker.patch("funkwhale_api.federation.actors.get_actor_data")
    new_actor = actors.get_actor(actor.fid)

    assert new_actor == actor
    get_data.assert_not_called()


def test_get_actor_refresh(factories, preferences, mocker):
    preferences["federation__actor_fetch_delay"] = 0
    actor = factories["federation.Actor"]()
    payload = serializers.ActorSerializer(actor).data
    # actor changed their username in the meantime
    payload["preferredUsername"] = "New me"
    mocker.patch("funkwhale_api.federation.actors.get_actor_data", return_value=payload)
    new_actor = actors.get_actor(actor.fid)

    assert new_actor == actor
    assert new_actor.last_fetch_date > actor.last_fetch_date
    assert new_actor.preferred_username == "New me"


def test_get_service_actor(db, settings):
    settings.FEDERATION_HOSTNAME = "test.hello"
    settings.FEDERATION_SERVICE_ACTOR_USERNAME = "bob"
    actor = actors.get_service_actor()

    assert actor.preferred_username == "bob"
    assert actor.domain.name == "test.hello"
    assert actor.private_key is not None
    assert actor.type == "Service"
    assert actor.public_key is not None
