from django.urls import reverse
from django.core.paginator import Paginator

import pytest

from funkwhale_api.federation import actors
from funkwhale_api.federation import serializers
from funkwhale_api.federation import utils
from funkwhale_api.federation import webfinger


@pytest.mark.parametrize('system_actor', actors.SYSTEM_ACTORS.keys())
def test_instance_actors(system_actor, db, settings, api_client):
    actor = actors.SYSTEM_ACTORS[system_actor].get_actor_instance()
    url = reverse(
        'federation:instance-actors-detail',
        kwargs={'actor': system_actor})
    response = api_client.get(url)
    serializer = serializers.ActorSerializer(actor)

    if system_actor == 'library':
        response.data.pop('url')
    assert response.status_code == 200
    assert response.data == serializer.data


@pytest.mark.parametrize('route,kwargs', [
    ('instance-actors-outbox', {'actor': 'library'}),
    ('instance-actors-inbox', {'actor': 'library'}),
    ('instance-actors-detail', {'actor': 'library'}),
    ('well-known-webfinger', {}),
])
def test_instance_endpoints_405_if_federation_disabled(
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
    actor = actors.SYSTEM_ACTORS[system_actor].get_actor_instance()
    url = reverse('federation:well-known-webfinger')
    response = api_client.get(
        url, data={'resource': 'acct:{}'.format(actor.webfinger_subject)})
    serializer = serializers.ActorWebfingerSerializer(actor)

    assert response.status_code == 200
    assert response['Content-Type'] == 'application/jrd+json'
    assert response.data == serializer.data


def test_audio_file_list_requires_authenticated_actor(
        db, settings, api_client):
    settings.FEDERATION_MUSIC_NEEDS_APPROVAL = True
    url = reverse('federation:music:files-list')
    response = api_client.get(url)

    assert response.status_code == 403


def test_audio_file_list_actor_no_page(
        db, settings, api_client, factories):
    settings.FEDERATION_MUSIC_NEEDS_APPROVAL = False
    settings.FEDERATION_COLLECTION_PAGE_SIZE = 2
    library = actors.SYSTEM_ACTORS['library'].get_actor_instance()
    tfs = factories['music.TrackFile'].create_batch(size=5)
    conf = {
        'id': utils.full_url(reverse('federation:music:files-list')),
        'page_size': 2,
        'items': list(reversed(tfs)),  # we order by -creation_date
        'item_serializer': serializers.AudioSerializer,
        'actor': library
    }
    expected = serializers.PaginatedCollectionSerializer(conf).data
    url = reverse('federation:music:files-list')
    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data == expected


def test_audio_file_list_actor_page(
        db, settings, api_client, factories):
    settings.FEDERATION_MUSIC_NEEDS_APPROVAL = False
    settings.FEDERATION_COLLECTION_PAGE_SIZE = 2
    library = actors.SYSTEM_ACTORS['library'].get_actor_instance()
    tfs = factories['music.TrackFile'].create_batch(size=5)
    conf = {
        'id': utils.full_url(reverse('federation:music:files-list')),
        'page': Paginator(list(reversed(tfs)), 2).page(2),
        'item_serializer': serializers.AudioSerializer,
        'actor': library
    }
    expected = serializers.CollectionPageSerializer(conf).data
    url = reverse('federation:music:files-list')
    response = api_client.get(url, data={'page': 2})

    assert response.status_code == 200
    assert response.data == expected


def test_audio_file_list_actor_page_exclude_federated_files(
        db, settings, api_client, factories):
    settings.FEDERATION_MUSIC_NEEDS_APPROVAL = False
    library = actors.SYSTEM_ACTORS['library'].get_actor_instance()
    tfs = factories['music.TrackFile'].create_batch(size=5, federation=True)

    url = reverse('federation:music:files-list')
    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data['totalItems'] == 0


def test_audio_file_list_actor_page_error(
        db, settings, api_client, factories):
    settings.FEDERATION_MUSIC_NEEDS_APPROVAL = False
    url = reverse('federation:music:files-list')
    response = api_client.get(url, data={'page': 'nope'})

    assert response.status_code == 400


def test_audio_file_list_actor_page_error_too_far(
        db, settings, api_client, factories):
    settings.FEDERATION_MUSIC_NEEDS_APPROVAL = False
    url = reverse('federation:music:files-list')
    response = api_client.get(url, data={'page': 5000})

    assert response.status_code == 404


def test_library_actor_includes_library_link(db, settings, api_client):
    actor = actors.SYSTEM_ACTORS['library'].get_actor_instance()
    url = reverse(
        'federation:instance-actors-detail',
        kwargs={'actor': 'library'})
    response = api_client.get(url)
    expected_links = [
        {
            'type': 'Link',
            'name': 'library',
            'mediaType': 'application/activity+json',
            'href': utils.full_url(reverse('federation:music:files-list'))
        }
    ]
    assert response.status_code == 200
    assert response.data['url'] == expected_links
