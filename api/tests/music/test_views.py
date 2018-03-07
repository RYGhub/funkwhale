import pytest

from funkwhale_api.music import views


@pytest.mark.parametrize('param,expected', [
    ('true', 'full'),
    ('false', 'empty'),
])
def test_artist_view_filter_listenable(
        param, expected, factories, api_request):
    artists = {
        'empty': factories['music.Artist'](),
        'full': factories['music.TrackFile']().track.artist,
    }

    request = api_request.get('/', {'listenable': param})
    view = views.ArtistViewSet()
    view.action_map = {'get': 'list'}
    expected = [artists[expected]]
    view.request = view.initialize_request(request)
    queryset = view.filter_queryset(view.get_queryset())

    assert list(queryset) == expected


@pytest.mark.parametrize('param,expected', [
    ('true', 'full'),
    ('false', 'empty'),
])
def test_album_view_filter_listenable(
        param, expected, factories, api_request):
    artists = {
        'empty': factories['music.Album'](),
        'full': factories['music.TrackFile']().track.album,
    }

    request = api_request.get('/', {'listenable': param})
    view = views.AlbumViewSet()
    view.action_map = {'get': 'list'}
    expected = [artists[expected]]
    view.request = view.initialize_request(request)
    queryset = view.filter_queryset(view.get_queryset())

    assert list(queryset) == expected
