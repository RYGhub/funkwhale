import pytest
from dynamic_preferences.registries import global_preferences_registry

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
