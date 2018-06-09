import django_filters

from funkwhale_api.common import serializers
from funkwhale_api.users import models


class TestActionFilterSet(django_filters.FilterSet):
    class Meta:
        model = models.User
        fields = ["is_active"]


class TestSerializer(serializers.ActionSerializer):
    actions = ["test"]
    filterset_class = TestActionFilterSet

    def handle_test(self, objects):
        return {"hello": "world"}


class TestDangerousSerializer(serializers.ActionSerializer):
    actions = ["test", "test_dangerous"]
    dangerous_actions = ["test_dangerous"]

    def handle_test(self, objects):
        pass

    def handle_test_dangerous(self, objects):
        pass


def test_action_serializer_validates_action():
    data = {"objects": "all", "action": "nope"}
    serializer = TestSerializer(data, queryset=models.User.objects.none())

    assert serializer.is_valid() is False
    assert "action" in serializer.errors


def test_action_serializer_validates_objects():
    data = {"objects": "nope", "action": "test"}
    serializer = TestSerializer(data, queryset=models.User.objects.none())

    assert serializer.is_valid() is False
    assert "objects" in serializer.errors


def test_action_serializers_objects_clean_ids(factories):
    user1 = factories["users.User"]()
    factories["users.User"]()

    data = {"objects": [user1.pk], "action": "test"}
    serializer = TestSerializer(data, queryset=models.User.objects.all())

    assert serializer.is_valid() is True
    assert list(serializer.validated_data["objects"]) == [user1]


def test_action_serializers_objects_clean_all(factories):
    user1 = factories["users.User"]()
    user2 = factories["users.User"]()

    data = {"objects": "all", "action": "test"}
    serializer = TestSerializer(data, queryset=models.User.objects.all())

    assert serializer.is_valid() is True
    assert list(serializer.validated_data["objects"]) == [user1, user2]


def test_action_serializers_save(factories, mocker):
    handler = mocker.spy(TestSerializer, "handle_test")
    factories["users.User"]()
    factories["users.User"]()

    data = {"objects": "all", "action": "test"}
    serializer = TestSerializer(data, queryset=models.User.objects.all())

    assert serializer.is_valid() is True
    result = serializer.save()
    assert result == {"updated": 2, "action": "test", "result": {"hello": "world"}}
    handler.assert_called_once()


def test_action_serializers_filterset(factories):
    factories["users.User"](is_active=False)
    user2 = factories["users.User"](is_active=True)

    data = {"objects": "all", "action": "test", "filters": {"is_active": True}}
    serializer = TestSerializer(data, queryset=models.User.objects.all())

    assert serializer.is_valid() is True
    assert list(serializer.validated_data["objects"]) == [user2]


def test_action_serializers_validates_at_least_one_object():
    data = {"objects": "all", "action": "test"}
    serializer = TestSerializer(data, queryset=models.User.objects.none())

    assert serializer.is_valid() is False
    assert "non_field_errors" in serializer.errors


def test_dangerous_actions_refuses_all(factories):
    factories["users.User"]()
    data = {"objects": "all", "action": "test_dangerous"}
    serializer = TestDangerousSerializer(data, queryset=models.User.objects.all())

    assert serializer.is_valid() is False
    assert "non_field_errors" in serializer.errors


def test_dangerous_actions_refuses_not_listed(factories):
    factories["users.User"]()
    data = {"objects": "all", "action": "test"}
    serializer = TestDangerousSerializer(data, queryset=models.User.objects.all())

    assert serializer.is_valid() is True
