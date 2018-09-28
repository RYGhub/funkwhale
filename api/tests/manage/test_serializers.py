from funkwhale_api.manage import serializers


def test_manage_upload_action_delete(factories):
    uploads = factories["music.Upload"](size=5)
    s = serializers.ManageUploadActionSerializer(queryset=None)

    s.handle_delete(uploads.__class__.objects.all())

    assert uploads.__class__.objects.count() == 0


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
        data={
            "is_active": False,
            "permissions": {"federation": False, "upload": True},
            "upload_quota": 12,
        },
    )
    s.is_valid(raise_exception=True)
    s.save()
    user.refresh_from_db()

    assert user.is_active is False
    assert user.upload_quota == 12
    assert user.permission_federation is False
    assert user.permission_upload is True
    assert user.permission_library is False
    assert user.permission_settings is True


def test_manage_import_request_mark_closed(factories):
    affected = factories["requests.ImportRequest"].create_batch(
        size=5, status="pending"
    )
    # we do not update imported requests
    factories["requests.ImportRequest"].create_batch(size=5, status="imported")
    s = serializers.ManageImportRequestActionSerializer(
        queryset=affected[0].__class__.objects.all(),
        data={"objects": "all", "action": "mark_closed"},
    )

    assert s.is_valid(raise_exception=True) is True
    s.save()

    assert affected[0].__class__.objects.filter(status="imported").count() == 5
    for ir in affected:
        ir.refresh_from_db()
        assert ir.status == "closed"


def test_manage_import_request_mark_imported(factories, now):
    affected = factories["requests.ImportRequest"].create_batch(
        size=5, status="pending"
    )
    # we do not update closed requests
    factories["requests.ImportRequest"].create_batch(size=5, status="closed")
    s = serializers.ManageImportRequestActionSerializer(
        queryset=affected[0].__class__.objects.all(),
        data={"objects": "all", "action": "mark_imported"},
    )

    assert s.is_valid(raise_exception=True) is True
    s.save()

    assert affected[0].__class__.objects.filter(status="closed").count() == 5
    for ir in affected:
        ir.refresh_from_db()
        assert ir.status == "imported"
        assert ir.imported_date == now
