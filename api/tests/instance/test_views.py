from django.urls import reverse


def test_nodeinfo_endpoint(db, api_client, mocker):
    payload = {
        'test': 'test'
    }
    mocked_nodeinfo = mocker.patch(
        'funkwhale_api.instance.nodeinfo.get', return_value=payload)
    url = reverse('api:v1:instance:nodeinfo-2.0')
    response = api_client.get(url)
    ct = 'application/json; profile=http://nodeinfo.diaspora.software/ns/schema/2.0#; charset=utf-8'  # noqa
    assert response.status_code == 200
    assert response['Content-Type'] == ct
    assert response.data == payload


def test_nodeinfo_endpoint_disabled(db, api_client, preferences):
    preferences['instance__nodeinfo_enabled'] = False
    url = reverse('api:v1:instance:nodeinfo-2.0')
    response = api_client.get(url)

    assert response.status_code == 404
