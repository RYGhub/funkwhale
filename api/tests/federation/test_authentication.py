from funkwhale_api.federation import authentication, keys


def test_authenticate(factories, mocker, api_request):
    private, public = keys.get_key_pair()
    actor_url = "https://test.federation/actor"
    mocker.patch(
        "funkwhale_api.federation.actors.get_actor_data",
        return_value={
            "id": actor_url,
            "type": "Person",
            "outbox": "https://test.com",
            "inbox": "https://test.com",
            "preferredUsername": "test",
            "publicKey": {
                "publicKeyPem": public.decode("utf-8"),
                "owner": actor_url,
                "id": actor_url + "#main-key",
            },
        },
    )
    signed_request = factories["federation.SignedRequest"](
        auth__key=private, auth__key_id=actor_url + "#main-key", auth__headers=["date"]
    )
    prepared = signed_request.prepare()
    django_request = api_request.get(
        "/",
        **{
            "HTTP_DATE": prepared.headers["date"],
            "HTTP_SIGNATURE": prepared.headers["signature"],
        }
    )
    authenticator = authentication.SignatureAuthentication()
    user, _ = authenticator.authenticate(django_request)
    actor = django_request.actor

    assert user.is_anonymous is True
    assert actor.public_key == public.decode("utf-8")
    assert actor.fid == actor_url
