import pytest

from django.urls import reverse

from funkwhale_api.common import preferences as common_preferences
from funkwhale_api.common import utils as common_utils


@pytest.mark.parametrize("value", [{"fields": {}}, {"fields": list(range(15))}])
def test_get_serialized_preference_error(value, preferences):
    pref_id = "moderation__signup_form_customization"

    with pytest.raises(common_preferences.JSONSerializer.exception):
        preferences[pref_id] = value


@pytest.mark.parametrize(
    "value",
    [
        {"fields": []},
        {"help_text": {"text": "hello", "content_type": "text/markdown"}},
        {"fields": [{"label": "Message", "required": True, "input_type": "long_text"}]},
    ],
)
def test_get_serialized_preference(value, preferences):
    pref_id = "moderation__signup_form_customization"

    preferences[pref_id] = value
    if "help_text" in value:
        value["help_text"]["html"] = common_utils.render_html(
            value["help_text"]["text"],
            content_type=value["help_text"]["content_type"],
            permissive=True,
        )
    assert preferences[pref_id] == value


def test_update_via_api(superuser_api_client, preferences):
    pref_id = "moderation__signup_form_customization"
    url = reverse("api:v1:instance:admin-settings-bulk")
    new_value = {
        "help_text": {"text": "hello", "content_type": "text/markdown"},
        "fields": [{"required": True, "label": "hello", "input_type": "short_text"}],
    }
    response = superuser_api_client.post(url, {pref_id: new_value}, format="json")
    assert response.status_code == 200
    new_value["help_text"]["html"] = common_utils.render_html(
        new_value["help_text"]["text"],
        content_type=new_value["help_text"]["content_type"],
        permissive=True,
    )
    assert preferences[pref_id] == new_value
