from funkwhale_api.playlists import serializers


def test_cannot_max_500_tracks_per_playlist(mocker, factories, settings):
    settings.PLAYLISTS_MAX_TRACKS = 2
    playlist = factories['playlists.Playlist']()
    plts = factories['playlists.PlaylistTrack'].create_batch(
        size=2, playlist=playlist)
    track = factories['music.Track']()
    serializer = serializers.PlaylistTrackCreateSerializer(data={
        'playlist': playlist.pk,
        'track': track.pk,
    })

    assert serializer.is_valid() is False
    assert 'playlist' in serializer.errors
