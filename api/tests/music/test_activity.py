from funkwhale_api.music import serializers
from funkwhale_api.music import signals


def test_get_track_activity_url_mbid(factories):
    track = factories["music.Track"]()
    expected = "https://musicbrainz.org/recording/{}".format(track.mbid)
    assert track.get_activity_url() == expected


def test_get_track_activity_url_no_mbid(settings, factories):
    track = factories["music.Track"](mbid=None)
    expected = settings.FUNKWHALE_URL + "/tracks/{}".format(track.pk)
    assert track.get_activity_url() == expected


def test_track_file_import_status_updated_broadcast(factories, mocker):
    group_send = mocker.patch("funkwhale_api.common.channels.group_send")
    user = factories["users.User"]()
    tf = factories["music.TrackFile"](
        import_status="finished", library__actor__user=user
    )
    signals.track_file_import_status_updated.send(
        sender=None, track_file=tf, old_status="pending", new_status="finished"
    )
    group_send.assert_called_once_with(
        "user.{}.imports".format(user.pk),
        {
            "type": "event.send",
            "text": "",
            "data": {
                "type": "import.status_updated",
                "old_status": "pending",
                "new_status": "finished",
                "track_file": serializers.TrackFileForOwnerSerializer(tf).data,
            },
        },
    )
