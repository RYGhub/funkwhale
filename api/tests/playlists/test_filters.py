from funkwhale_api.playlists import filters
from funkwhale_api.playlists import models


def test_playlist_filter_track(factories, queryset_equal_list):
    plt = factories["playlists.PlaylistTrack"]()
    factories["playlists.PlaylistTrack"]()
    qs = models.Playlist.objects.all()
    filterset = filters.PlaylistFilter({"track": plt.track.pk}, queryset=qs)

    assert filterset.qs == [plt.playlist]


def test_playlist_filter_album(factories, queryset_equal_list):
    plt = factories["playlists.PlaylistTrack"]()
    factories["playlists.PlaylistTrack"]()
    qs = models.Playlist.objects.all()
    filterset = filters.PlaylistFilter({"album": plt.track.album.pk}, queryset=qs)

    assert filterset.qs == [plt.playlist]


def test_playlist_filter_artist(factories, queryset_equal_list):
    plt = factories["playlists.PlaylistTrack"]()
    factories["playlists.PlaylistTrack"]()
    qs = models.Playlist.objects.all()
    filterset = filters.PlaylistFilter({"artist": plt.track.artist.pk}, queryset=qs)

    assert filterset.qs == [plt.playlist]
