

def test_can_create_playlist(factories):
    tracks = factories['music.Track'].create_batch(5)
    playlist = factories['playlists.Playlist']()

    previous = None
    for track in tracks:
        previous = playlist.add_track(track, previous=previous)

    playlist_tracks = list(playlist.playlist_tracks.all())

    previous = None
    for idx, track in enumerate(tracks):
        plt = playlist_tracks[idx]
        assert plt.position == idx
        assert plt.track == track
        if previous:
            assert playlist_tracks[idx + 1] == previous
        assert plt.playlist == playlist
