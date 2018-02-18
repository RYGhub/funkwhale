from django.urls import reverse

from dynamic_preferences.api import serializers


def test_can_list_settings_via_api(preferences, api_client):
    url = reverse('api:v1:instance:settings')
    all_preferences = preferences.model.objects.all()
    expected_preferences = {
        p.preference.identifier(): p
        for p in all_preferences
        if getattr(p.preference, 'show_in_api', False)}

    assert len(expected_preferences) > 0

    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == len(expected_preferences)

    for p in response.data:
        i = '__'.join([p['section'], p['name']])
        assert i in expected_preferences
