from django.urls import reverse

import pytest

from funkwhale_api.federation import webfinger


def test_instance_actor(db, settings, api_client):
    settings.FUNKWHALE_URL = 'http://test.com'
    url = reverse('federation:instance-actor')
    response = api_client.get(url)
    assert response.data['id'] == (
      settings.FUNKWHALE_URL + url
    )
    assert response.data['type'] == 'Service'
    assert response.data['inbox'] == (
      settings.FUNKWHALE_URL + reverse('federation:instance-inbox')
    )
    assert response.data['outbox'] == (
      settings.FUNKWHALE_URL + reverse('federation:instance-outbox')
    )
    assert response.data['@context'] == [
      'https://www.w3.org/ns/activitystreams',
      'https://w3id.org/security/v1',
      {},
    ]


@pytest.mark.parametrize('route', [
    'instance-outbox',
    'instance-inbox',
    'instance-actor',
    'well-known-webfinger',
])
def test_instance_inbox_405_if_federation_disabled(
        db, settings, api_client, route):
    settings.FEDERATION_ENABLED = False
    url = reverse('federation:{}'.format(route))
    response = api_client.get(url)

    assert response.status_code == 405


def test_wellknown_webfinger_validates_resource(
    db, api_client, settings, mocker):
    clean = mocker.spy(webfinger, 'clean_resource')
    settings.FEDERATION_ENABLED = True
    url = reverse('federation:well-known-webfinger')
    response = api_client.get(url, data={'resource': 'something'})

    clean.assert_called_once_with('something')
    assert url == '/.well-known/webfinger'
    assert response.status_code == 400
    assert response.data['errors']['resource'] == (
        'Missing webfinger resource type'
    )


def test_wellknown_webfinger_system(
    db, api_client, settings, mocker):
    settings.FEDERATION_ENABLED = True
    settings.FEDERATION_HOSTNAME = 'test.federation'
    url = reverse('federation:well-known-webfinger')
    response = api_client.get(
        url, data={'resource': 'acct:service@test.federation'})

    assert response.status_code == 200
    assert response['Content-Type'] == 'application/jrd+json; charset=utf-8'
    assert response.data == webfinger.serialize_system_acct()
