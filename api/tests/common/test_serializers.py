import django_filters

from funkwhale_api.common import serializers
from funkwhale_api.users import models


class TestActionFilterSet(django_filters.FilterSet):
    class Meta:
        model = models.User
        fields = ['is_active']


class TestSerializer(serializers.ActionSerializer):
    actions = ['test']
    filterset_class = TestActionFilterSet

    def handle_test(self, objects):
        return {'hello': 'world'}


def test_action_serializer_validates_action():
    data = {'objects': 'all', 'action': 'nope'}
    serializer = TestSerializer(data, queryset=models.User.objects.none())

    assert serializer.is_valid() is False
    assert 'action' in serializer.errors


def test_action_serializer_validates_objects():
    data = {'objects': 'nope', 'action': 'test'}
    serializer = TestSerializer(data, queryset=models.User.objects.none())

    assert serializer.is_valid() is False
    assert 'objects' in serializer.errors


def test_action_serializers_objects_clean_ids(factories):
    user1 = factories['users.User']()
    user2 = factories['users.User']()

    data = {'objects': [user1.pk], 'action': 'test'}
    serializer = TestSerializer(data, queryset=models.User.objects.all())

    assert serializer.is_valid() is True
    assert list(serializer.validated_data['objects']) == [user1]


def test_action_serializers_objects_clean_all(factories):
    user1 = factories['users.User']()
    user2 = factories['users.User']()

    data = {'objects': 'all', 'action': 'test'}
    serializer = TestSerializer(data, queryset=models.User.objects.all())

    assert serializer.is_valid() is True
    assert list(serializer.validated_data['objects']) == [user1, user2]


def test_action_serializers_save(factories, mocker):
    handler = mocker.spy(TestSerializer, 'handle_test')
    user1 = factories['users.User']()
    user2 = factories['users.User']()

    data = {'objects': 'all', 'action': 'test'}
    serializer = TestSerializer(data, queryset=models.User.objects.all())

    assert serializer.is_valid() is True
    result = serializer.save()
    assert result == {
        'updated': 2,
        'action': 'test',
        'result': {'hello': 'world'},
    }
    handler.assert_called_once()


def test_action_serializers_filterset(factories):
    user1 = factories['users.User'](is_active=False)
    user2 = factories['users.User'](is_active=True)

    data = {
        'objects': 'all',
        'action': 'test',
        'filters': {'is_active': True},
    }
    serializer = TestSerializer(data, queryset=models.User.objects.all())

    assert serializer.is_valid() is True
    assert list(serializer.validated_data['objects']) == [user2]
