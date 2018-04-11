from django.core.paginator import Paginator

from funkwhale_api.federation import serializers
from funkwhale_api.federation import tasks


def test_scan_library_does_nothing_if_federation_disabled(mocker, factories):
    library = factories['federation.Library'](federation_enabled=False)
    tasks.scan_library(library_id=library.pk)

    assert library.tracks.count() == 0


def test_scan_library_page_does_nothing_if_federation_disabled(
        mocker, factories):
    library = factories['federation.Library'](federation_enabled=False)
    tasks.scan_library_page(library_id=library.pk, page_url=None)

    assert library.tracks.count() == 0


def test_scan_library_fetches_page_and_calls_scan_page(
        mocker, factories, r_mock):
    library = factories['federation.Library'](federation_enabled=True)
    collection_conf = {
        'actor': library.actor,
        'id': library.url,
        'page_size': 10,
        'items': range(10),
    }
    collection = serializers.PaginatedCollectionSerializer(collection_conf)
    scan_page = mocker.patch(
        'funkwhale_api.federation.tasks.scan_library_page.delay')
    r_mock.get(collection_conf['id'], json=collection.data)
    tasks.scan_library(library_id=library.pk)

    scan_page.assert_called_once_with(
        library_id=library.id,
        page_url=collection.data['first'],
    )


def test_scan_page_fetches_page_and_creates_tracks(
        mocker, factories, r_mock):
    library = factories['federation.Library'](federation_enabled=True)
    tfs = factories['music.TrackFile'].create_batch(size=5)
    page_conf = {
        'actor': library.actor,
        'id': library.url,
        'page': Paginator(tfs, 5).page(1),
        'item_serializer': serializers.AudioSerializer,
    }
    page = serializers.CollectionPageSerializer(page_conf)
    #scan_page = mocker.patch(
    #    'funkwhale_api.federation.tasks.scan_library_page.delay')
    r_mock.get(page.data['id'], json=page.data)

    tasks.scan_library_page(library_id=library.pk, page_url=page.data['id'])

    lts = list(library.tracks.all().order_by('-published_date'))
    assert len(lts) == 5
