import pytest

from dynamic_preferences import types
from dynamic_preferences.registries import global_preferences_registry

from rest_framework import serializers

from funkwhale_api.common import preferences as common_preferences


@pytest.fixture
def string_list_pref(preferences):
    @global_preferences_registry.register
    class P(common_preferences.StringListPreference):
        default = ["hello"]
        section = "test"
        name = "string_list"

    yield
    del global_preferences_registry["test"]["string_list"]


@pytest.mark.parametrize(
    "input,output",
    [
        (["a", "b", "c"], "a,b,c"),
        (["a", "c", "b"], "a,b,c"),
        (("a", "c", "b"), "a,b,c"),
        ([], None),
    ],
)
def test_string_list_serializer_to_db(input, output):
    common_preferences.StringListSerializer.to_db(input) == output


@pytest.mark.parametrize(
    "input,output", [("a,b,c", ["a", "b", "c"]), (None, []), ("", [])]
)
def test_string_list_serializer_to_python(input, output):
    common_preferences.StringListSerializer.to_python(input) == output


def test_string_list_pref_default(string_list_pref, preferences):
    assert preferences["test__string_list"] == ["hello"]


def test_string_list_pref_set(string_list_pref, preferences):
    preferences["test__string_list"] = ["world", "hello"]
    assert preferences["test__string_list"] == ["hello", "world"]


class PreferenceDataSerializer(serializers.Serializer):
    name = serializers.CharField()
    optional = serializers.BooleanField(required=False)


@pytest.fixture
def serialized_preference(db):
    @global_preferences_registry.register
    class TestSerialized(common_preferences.SerializedPreference):
        section = types.Section("test")
        name = "serialized"
        data_serializer_class = PreferenceDataSerializer
        default = None
        required = False

    yield
    del global_preferences_registry["test"]["serialized"]


@pytest.mark.parametrize(
    "value", [{"name": "hello"}, {"name": "hello", "optional": True}]
)
def test_get_serialized_preference(value, preferences, serialized_preference):
    pref_id = "test__serialized"
    # default value
    assert preferences[pref_id] is None

    preferences[pref_id] = value
    assert preferences[pref_id] == value


@pytest.mark.parametrize(
    "value", [{"noop": "hello"}, {"name": "hello", "optional": None}, "noop"]
)
def test_get_serialized_preference_error(value, preferences, serialized_preference):
    pref_id = "test__serialized"

    with pytest.raises(common_preferences.JSONSerializer.exception):
        preferences[pref_id] = value
