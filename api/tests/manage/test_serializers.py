from funkwhale_api.manage import serializers


def test_manage_track_file_action_delete(factories):
    tfs = factories["music.TrackFile"](size=5)
    s = serializers.ManageTrackFileActionSerializer(queryset=None)

    s.handle_delete(tfs.__class__.objects.all())

    assert tfs.__class__.objects.count() == 0


def test_user_update_permission(factories):
    user = factories["users.User"](
        permission_library=False,
        permission_upload=False,
        permission_federation=True,
        permission_settings=True,
        is_active=True,
    )
    s = serializers.ManageUserSerializer(
        user,
        data={"is_active": False, "permissions": {"federation": False, "upload": True}},
    )
    s.is_valid(raise_exception=True)
    s.save()
    user.refresh_from_db()

    assert user.is_active is False
    assert user.permission_federation is False
    assert user.permission_upload is True
    assert user.permission_library is False
    assert user.permission_settings is True
