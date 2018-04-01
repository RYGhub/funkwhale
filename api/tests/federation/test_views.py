from django.urls import reverse

import pytest

from funkwhale_api.federation import actors
from funkwhale_api.federation import serializers
from funkwhale_api.federation import webfinger



@pytest.mark.parametrize('system_actor', actors.SYSTEM_ACTORS.keys())
def test_instance_actors(system_actor, db, settings, api_client):
    actor = actors.SYSTEM_ACTORS[system_actor]['get_actor']()
    url = reverse(
        'federation:instance-actors-detail',
        kwargs={'actor': system_actor})
    response = api_client.get(url)
    serializer = serializers.ActorSerializer(actor)

    assert response.status_code == 200
    assert response.data == serializer.data


@pytest.mark.parametrize('route,kwargs', [
    ('instance-actors-outbox', {'actor': 'library'}),
    ('instance-actors-inbox', {'actor': 'library'}),
    ('instance-actors-detail', {'actor': 'library'}),
    ('well-known-webfinger', {}),
])
def test_instance_inbox_405_if_federation_disabled(
        authenticated_actor, db, settings, api_client, route, kwargs):
    settings.FEDERATION_ENABLED = False
    url = reverse('federation:{}'.format(route), kwargs=kwargs)
    response = api_client.get(url)

    assert response.status_code == 405


def test_wellknown_webfinger_validates_resource(
    db, api_client, settings, mocker):
    clean = mocker.spy(webfinger, 'clean_resource')
    url = reverse('federation:well-known-webfinger')
    response = api_client.get(url, data={'resource': 'something'})

    clean.assert_called_once_with('something')
    assert url == '/.well-known/webfinger'
    assert response.status_code == 400
    assert response.data['errors']['resource'] == (
        'Missing webfinger resource type'
    )


@pytest.mark.parametrize('system_actor', actors.SYSTEM_ACTORS.keys())
def test_wellknown_webfinger_system(
        system_actor, db, api_client, settings, mocker):
    actor = actors.SYSTEM_ACTORS[system_actor]['get_actor']()
    url = reverse('federation:well-known-webfinger')
    response = api_client.get(
        url, data={'resource': 'acct:{}'.format(actor.webfinger_subject)})
    serializer = serializers.ActorWebfingerSerializer(actor)

    assert response.status_code == 200
    assert response['Content-Type'] == 'application/jrd+json'
    assert response.data == serializer.data
