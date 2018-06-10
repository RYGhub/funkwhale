

def test_get_track_activity_url_mbid(factories):
    track = factories["music.Track"]()
    expected = "https://musicbrainz.org/recording/{}".format(track.mbid)
    assert track.get_activity_url() == expected


def test_get_track_activity_url_no_mbid(settings, factories):
    track = factories["music.Track"](mbid=None)
    expected = settings.FUNKWHALE_URL + "/tracks/{}".format(track.pk)
    assert track.get_activity_url() == expected
