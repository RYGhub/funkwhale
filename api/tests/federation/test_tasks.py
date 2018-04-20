import datetime

from django.core.paginator import Paginator
from django.utils import timezone

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
    now = timezone.now()
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
        until=None,
    )
    library.refresh_from_db()
    assert library.fetched_date > now


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
    r_mock.get(page.data['id'], json=page.data)

    tasks.scan_library_page(library_id=library.pk, page_url=page.data['id'])

    lts = list(library.tracks.all().order_by('-published_date'))
    assert len(lts) == 5


def test_scan_page_trigger_next_page_scan_skip_if_same(
        mocker, factories, r_mock):
    patched_scan = mocker.patch(
        'funkwhale_api.federation.tasks.scan_library_page.delay'
    )
    library = factories['federation.Library'](federation_enabled=True)
    tfs = factories['music.TrackFile'].create_batch(size=1)
    page_conf = {
        'actor': library.actor,
        'id': library.url,
        'page': Paginator(tfs, 3).page(1),
        'item_serializer': serializers.AudioSerializer,
    }
    page = serializers.CollectionPageSerializer(page_conf)
    data = page.data
    data['next'] = data['id']
    r_mock.get(page.data['id'], json=data)

    tasks.scan_library_page(library_id=library.pk, page_url=data['id'])
    patched_scan.assert_not_called()


def test_scan_page_stops_once_until_is_reached(
        mocker, factories, r_mock):
    library = factories['federation.Library'](federation_enabled=True)
    tfs = list(reversed(factories['music.TrackFile'].create_batch(size=5)))
    page_conf = {
        'actor': library.actor,
        'id': library.url,
        'page': Paginator(tfs, 3).page(1),
        'item_serializer': serializers.AudioSerializer,
    }
    page = serializers.CollectionPageSerializer(page_conf)
    r_mock.get(page.data['id'], json=page.data)

    tasks.scan_library_page(
        library_id=library.pk,
        page_url=page.data['id'],
        until=tfs[1].creation_date)

    lts = list(library.tracks.all().order_by('-published_date'))
    assert len(lts) == 2
    for i, tf in enumerate(tfs[:1]):
        assert tf.creation_date == lts[i].published_date


def test_clean_federation_music_cache_if_no_listen(preferences, factories):
    preferences['federation__music_cache_duration'] = 60
    lt1 = factories['federation.LibraryTrack'](with_audio_file=True)
    lt2 = factories['federation.LibraryTrack'](with_audio_file=True)
    lt3 = factories['federation.LibraryTrack'](with_audio_file=True)
    tf1 = factories['music.TrackFile'](library_track=lt1)
    tf2 = factories['music.TrackFile'](library_track=lt2)
    tf3 = factories['music.TrackFile'](library_track=lt3)

    # we listen to the first one, and the second one (but weeks ago)
    listening1 = factories['history.Listening'](
        track=tf1.track,
        creation_date=timezone.now())
    listening2 = factories['history.Listening'](
        track=tf2.track,
        creation_date=timezone.now() - datetime.timedelta(minutes=61))

    tasks.clean_music_cache()

    lt1.refresh_from_db()
    lt2.refresh_from_db()
    lt3.refresh_from_db()

    assert bool(lt1.audio_file) is True
    assert bool(lt2.audio_file) is False
    assert bool(lt3.audio_file) is False