import pytest

from funkwhale_api.common import mutations

from rest_framework import serializers


@pytest.fixture
def mutations_registry():
    return mutations.Registry()


def test_apply_mutation(mutations_registry, db):
    class Obj:
        pass

    obj = Obj()

    @mutations_registry.connect("foo", Obj)
    class S(mutations.MutationSerializer):
        foo = serializers.ChoiceField(choices=["bar", "baz"])

        def apply(self, obj, validated_data):
            setattr(obj, "foo", validated_data["foo"])

    with pytest.raises(mutations.ConfNotFound):
        mutations_registry.apply("foo", object(), payload={"foo": "nope"})

    with pytest.raises(serializers.ValidationError):
        mutations_registry.apply("foo", obj, payload={"foo": "nope"})

    mutations_registry.apply("foo", obj, payload={"foo": "bar"})

    assert obj.foo == "bar"


def test_apply_update_mutation(factories, mutations_registry, mocker):
    user = factories["users.User"](email="hello@test.email")
    get_update_previous_state = mocker.patch.object(
        mutations, "get_update_previous_state"
    )

    @mutations_registry.connect("update", user.__class__)
    class S(mutations.UpdateMutationSerializer):
        class Meta:
            model = user.__class__
            fields = ["username", "email"]

    previous_state = mutations_registry.apply(
        "update", user, payload={"username": "foo"}
    )
    assert previous_state == get_update_previous_state.return_value
    get_update_previous_state.assert_called_once_with(
        user, "username", serialized_relations={}, handlers={}
    )
    user.refresh_from_db()

    assert user.username == "foo"
    assert user.email == "hello@test.email"


def test_db_serialize_update_mutation(factories, mutations_registry, mocker):
    user = factories["users.User"](email="hello@test.email", with_actor=True)

    class S(mutations.UpdateMutationSerializer):
        serialized_relations = {"actor": "full_username"}

        class Meta:
            model = user.__class__
            fields = ["actor"]

    expected = {"actor": user.actor.full_username}
    assert S().db_serialize({"actor": user.actor}) == expected


def test_is_valid_mutation(factories, mutations_registry):
    user = factories["users.User"].build()

    @mutations_registry.connect("update", user.__class__)
    class S(mutations.UpdateMutationSerializer):
        class Meta:
            model = user.__class__
            fields = ["email"]

    with pytest.raises(serializers.ValidationError):
        mutations_registry.is_valid("update", user, payload={"email": "foo"})
    mutations_registry.is_valid("update", user, payload={"email": "foo@bar.com"})


@pytest.mark.parametrize("perm", ["approve", "suggest"])
def test_permissions(perm, factories, mutations_registry, mocker):
    actor = factories["federation.Actor"].build()
    user = factories["users.User"].build()

    class S(mutations.UpdateMutationSerializer):
        class Meta:
            model = user.__class__
            fields = ["email"]

    mutations_registry.connect("update", user.__class__)(S)

    assert mutations_registry.has_perm(perm, "update", obj=user, actor=actor) is False

    checker = mocker.Mock(return_value=True)
    mutations_registry.connect("update", user.__class__, perm_checkers={perm: checker})(
        S
    )

    assert mutations_registry.has_perm(perm, "update", obj=user, actor=actor) is True
    checker.assert_called_once_with(obj=user, actor=actor)


def test_model_apply(factories, mocker, now):
    target = factories["music.Artist"]()
    mutation = factories["common.Mutation"](type="noop", target=target, payload="hello")

    apply = mocker.patch.object(
        mutations.registry, "apply", return_value={"previous": "state"}
    )

    mutation.apply()
    apply.assert_called_once_with(type="noop", obj=target, payload="hello")
    mutation.refresh_from_db()

    assert mutation.is_applied is True
    assert mutation.previous_state == {"previous": "state"}
    assert mutation.applied_date == now


def test_get_previous_state(factories):
    obj = factories["music.Track"]()
    expected = {
        "title": {"value": obj.title},
        "album": {"value": obj.album.pk, "repr": str(obj.album)},
    }
    assert (
        mutations.get_update_previous_state(
            obj, "title", "album", serialized_relations={"album": "pk"}
        )
        == expected
    )
