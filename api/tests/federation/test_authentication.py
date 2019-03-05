import pytest

from funkwhale_api.federation import authentication, exceptions, keys, jsonld


def test_authenticate(factories, mocker, api_request):
    private, public = keys.get_key_pair()
    factories["federation.Domain"](name="test.federation", nodeinfo_fetch_date=None)
    actor_url = "https://test.federation/actor"
    mocker.patch(
        "funkwhale_api.federation.actors.get_actor_data",
        return_value={
            "@context": jsonld.get_default_context(),
            "id": actor_url,
            "type": "Person",
            "outbox": "https://test.com",
            "inbox": "https://test.com",
            "followers": "https://test.com",
            "preferredUsername": "test",
            "publicKey": {
                "publicKeyPem": public.decode("utf-8"),
                "owner": actor_url,
                "id": actor_url + "#main-key",
            },
        },
    )
    update_domain_nodeinfo = mocker.patch(
        "funkwhale_api.federation.tasks.update_domain_nodeinfo"
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
    update_domain_nodeinfo.assert_called_once_with(domain_name="test.federation")


def test_authenticate_skips_blocked_domain(factories, api_request):
    policy = factories["moderation.InstancePolicy"](block_all=True, for_domain=True)
    private, public = keys.get_key_pair()
    actor_url = "https://{}/actor".format(policy.target_domain.name)

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

    with pytest.raises(exceptions.BlockedActorOrDomain):
        authenticator.authenticate(django_request)


def test_authenticate_skips_blocked_actor(factories, api_request):
    policy = factories["moderation.InstancePolicy"](block_all=True, for_actor=True)
    private, public = keys.get_key_pair()
    actor_url = policy.target_actor.fid

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

    with pytest.raises(exceptions.BlockedActorOrDomain):
        authenticator.authenticate(django_request)


def test_authenticate_ignore_inactive_policy(factories, api_request, mocker):
    policy = factories["moderation.InstancePolicy"](
        block_all=True, for_domain=True, is_active=False
    )
    private, public = keys.get_key_pair()
    actor_url = "https://{}/actor".format(policy.target_domain.name)

    signed_request = factories["federation.SignedRequest"](
        auth__key=private, auth__key_id=actor_url + "#main-key", auth__headers=["date"]
    )
    mocker.patch(
        "funkwhale_api.federation.actors.get_actor_data",
        return_value={
            "@context": jsonld.get_default_context(),
            "id": actor_url,
            "type": "Person",
            "outbox": "https://test.com",
            "inbox": "https://test.com",
            "followers": "https://test.com",
            "preferredUsername": "test",
            "publicKey": {
                "publicKeyPem": public.decode("utf-8"),
                "owner": actor_url,
                "id": actor_url + "#main-key",
            },
        },
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
    authenticator.authenticate(django_request)
    actor = django_request.actor

    assert actor.public_key == public.decode("utf-8")
    assert actor.fid == actor_url


def test_autenthicate_supports_blind_key_rotation(factories, mocker, api_request):
    actor = factories["federation.Actor"]()
    actor_url = actor.fid
    # request is signed with a pair of new keys
    new_private, new_public = keys.get_key_pair()
    mocker.patch(
        "funkwhale_api.federation.actors.get_actor_data",
        return_value={
            "@context": jsonld.get_default_context(),
            "id": actor_url,
            "type": "Person",
            "outbox": "https://test.com",
            "inbox": "https://test.com",
            "followers": "https://test.com",
            "preferredUsername": "test",
            "publicKey": {
                "publicKeyPem": new_public.decode("utf-8"),
                "owner": actor_url,
                "id": actor_url + "#main-key",
            },
        },
    )
    signed_request = factories["federation.SignedRequest"](
        auth__key=new_private,
        auth__key_id=actor_url + "#main-key",
        auth__headers=["date"],
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
    assert actor.public_key == new_public.decode("utf-8")
    assert actor.fid == actor_url
