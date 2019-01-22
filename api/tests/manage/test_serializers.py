import pytest

from funkwhale_api.manage import serializers
from funkwhale_api.federation import tasks as federation_tasks


def test_manage_upload_action_delete(factories):
    uploads = factories["music.Upload"](size=5)
    s = serializers.ManageUploadActionSerializer(queryset=None)

    s.handle_delete(uploads.__class__.objects.all())

    assert uploads.__class__.objects.count() == 0


def test_user_update_permission(factories):
    user = factories["users.User"](
        permission_library=False,
        permission_moderation=False,
        permission_settings=True,
        is_active=True,
    )
    s = serializers.ManageUserSerializer(
        user,
        data={
            "is_active": False,
            "permissions": {"moderation": True, "settings": False},
            "upload_quota": 12,
        },
    )
    s.is_valid(raise_exception=True)
    s.save()
    user.refresh_from_db()

    assert user.is_active is False
    assert user.upload_quota == 12
    assert user.permission_moderation is True
    assert user.permission_library is False
    assert user.permission_settings is False


def test_manage_domain_serializer(factories, now):
    domain = factories["federation.Domain"]()
    setattr(domain, "actors_count", 42)
    setattr(domain, "outbox_activities_count", 23)
    expected = {
        "name": domain.name,
        "creation_date": domain.creation_date.isoformat().split("+")[0] + "Z",
        "actors_count": 42,
        "outbox_activities_count": 23,
        "nodeinfo": {},
        "nodeinfo_fetch_date": None,
        "instance_policy": None,
    }
    s = serializers.ManageDomainSerializer(domain)

    assert s.data == expected


def test_manage_domain_serializer_validates_hostname(db):
    s = serializers.ManageDomainSerializer(data={"name": "hello world"})

    with pytest.raises(serializers.serializers.ValidationError):
        s.is_valid(raise_exception=True)


def test_manage_actor_serializer(factories, now):
    actor = factories["federation.Actor"]()
    setattr(actor, "uploads_count", 66)
    expected = {
        "id": actor.id,
        "name": actor.name,
        "creation_date": actor.creation_date.isoformat().split("+")[0] + "Z",
        "last_fetch_date": actor.last_fetch_date.isoformat().split("+")[0] + "Z",
        "uploads_count": 66,
        "fid": actor.fid,
        "url": actor.url,
        "outbox_url": actor.outbox_url,
        "shared_inbox_url": actor.shared_inbox_url,
        "inbox_url": actor.inbox_url,
        "domain": actor.domain_id,
        "type": actor.type,
        "summary": actor.summary,
        "preferred_username": actor.preferred_username,
        "manually_approves_followers": actor.manually_approves_followers,
        "full_username": actor.full_username,
        "user": None,
        "instance_policy": None,
    }
    s = serializers.ManageActorSerializer(actor)

    assert s.data == expected


@pytest.mark.parametrize(
    "factory_kwargs,expected",
    [
        (
            {"for_domain": True, "target_domain__name": "test.federation"},
            {"target": {"type": "domain", "id": "test.federation"}},
        ),
        (
            {
                "for_actor": True,
                "target_actor__domain__name": "test.federation",
                "target_actor__preferred_username": "hello",
            },
            {"target": {"type": "actor", "id": "hello@test.federation"}},
        ),
    ],
)
def test_instance_policy_serializer_repr(factories, factory_kwargs, expected):
    policy = factories["moderation.InstancePolicy"](block_all=True, **factory_kwargs)

    e = {
        "id": policy.id,
        "uuid": str(policy.uuid),
        "creation_date": policy.creation_date.isoformat().split("+")[0] + "Z",
        "actor": policy.actor.full_username,
        "block_all": True,
        "silence_activity": False,
        "silence_notifications": False,
        "reject_media": False,
        "is_active": policy.is_active,
        "summary": policy.summary,
    }
    e.update(expected)

    assert serializers.ManageInstancePolicySerializer(policy).data == e


def test_instance_policy_serializer_save_domain(factories):
    domain = factories["federation.Domain"]()

    data = {"target": {"id": domain.name, "type": "domain"}, "block_all": True}

    serializer = serializers.ManageInstancePolicySerializer(data=data)
    serializer.is_valid(raise_exception=True)
    policy = serializer.save()

    assert policy.target_domain == domain


def test_instance_policy_serializer_save_actor(factories):
    actor = factories["federation.Actor"]()

    data = {"target": {"id": actor.full_username, "type": "actor"}, "block_all": True}

    serializer = serializers.ManageInstancePolicySerializer(data=data)
    serializer.is_valid(raise_exception=True)
    policy = serializer.save()

    assert policy.target_actor == actor


def test_manage_actor_action_purge(factories, mocker):
    actors = factories["federation.Actor"].create_batch(size=3)
    s = serializers.ManageActorActionSerializer(queryset=None)
    on_commit = mocker.patch("funkwhale_api.common.utils.on_commit")

    s.handle_purge(actors[0].__class__.objects.all())
    on_commit.assert_called_once_with(
        federation_tasks.purge_actors.delay, ids=[a.pk for a in actors]
    )


def test_manage_domain_action_purge(factories, mocker):
    domains = factories["federation.Domain"].create_batch(size=3)
    s = serializers.ManageDomainActionSerializer(queryset=None)
    on_commit = mocker.patch("funkwhale_api.common.utils.on_commit")

    s.handle_purge(domains[0].__class__.objects.all())
    on_commit.assert_called_once_with(
        federation_tasks.purge_actors.delay, domains=[d.pk for d in domains]
    )


@pytest.mark.parametrize(
    "param,expected_only", [("block_all", []), ("reject_media", ["media"])]
)
def test_instance_policy_serializer_purges_target_domain(
    factories, mocker, param, expected_only
):
    params = {param: False}
    if param != "block_all":
        params["block_all"] = False
    policy = factories["moderation.InstancePolicy"](for_domain=True, **params)
    on_commit = mocker.patch("funkwhale_api.common.utils.on_commit")

    serializer = serializers.ManageInstancePolicySerializer(
        policy, data={param: True}, partial=True
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()

    policy.refresh_from_db()

    assert getattr(policy, param) is True
    on_commit.assert_called_once_with(
        federation_tasks.purge_actors.delay,
        domains=[policy.target_domain_id],
        only=expected_only,
    )

    on_commit.reset_mock()

    # setting to false should have no effect
    serializer = serializers.ManageInstancePolicySerializer(
        policy, data={param: False}, partial=True
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()

    policy.refresh_from_db()

    assert getattr(policy, param) is False
    assert on_commit.call_count == 0


@pytest.mark.parametrize(
    "param,expected_only", [("block_all", []), ("reject_media", ["media"])]
)
def test_instance_policy_serializer_purges_target_actor(
    factories, mocker, param, expected_only
):
    params = {param: False}
    if param != "block_all":
        params["block_all"] = False
    policy = factories["moderation.InstancePolicy"](for_actor=True, **params)
    on_commit = mocker.patch("funkwhale_api.common.utils.on_commit")

    serializer = serializers.ManageInstancePolicySerializer(
        policy, data={param: True}, partial=True
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()

    policy.refresh_from_db()

    assert getattr(policy, param) is True
    on_commit.assert_called_once_with(
        federation_tasks.purge_actors.delay,
        ids=[policy.target_actor_id],
        only=expected_only,
    )

    on_commit.reset_mock()

    # setting to false should have no effect
    serializer = serializers.ManageInstancePolicySerializer(
        policy, data={param: False}, partial=True
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()

    policy.refresh_from_db()

    assert getattr(policy, param) is False
    assert on_commit.call_count == 0
