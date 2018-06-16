from funkwhale_api.manage import serializers


def test_manage_track_file_action_delete(factories):
    tfs = factories["music.TrackFile"](size=5)
    s = serializers.ManageTrackFileActionSerializer(queryset=None)

    s.handle_delete(tfs.__class__.objects.all())

    assert tfs.__class__.objects.count() == 0
