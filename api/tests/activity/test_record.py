import pytest

from django.db import models
from rest_framework import serializers

from funkwhale_api.activity import record


class FakeModel(models.Model):
    class Meta:
        app_label = 'tests'


class FakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FakeModel
        fields = ['id']




def test_can_bind_serializer_to_model(activity_registry):
    activity_registry.register_serializer(FakeSerializer)

    assert activity_registry['tests.FakeModel']['serializer'] == FakeSerializer


def test_can_bind_consumer_to_model(activity_registry):
    activity_registry.register_serializer(FakeSerializer)
    @activity_registry.register_consumer('tests.FakeModel')
    def propagate(data, obj):
        return True

    assert activity_registry['tests.FakeModel']['consumers'] == [propagate]


def test_record_object_calls_consumer(activity_registry, mocker):
    activity_registry.register_serializer(FakeSerializer)
    stub = mocker.stub()
    activity_registry.register_consumer('tests.FakeModel')(stub)
    o = FakeModel(id=1)
    data = FakeSerializer(o).data
    record.send(o)

    stub.assert_called_once_with(data=data, obj=o)
