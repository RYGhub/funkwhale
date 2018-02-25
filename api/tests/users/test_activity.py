from funkwhale_api.users import serializers


def test_get_user_activity_url(settings, factories):
    user = factories['users.User']()
    assert user.get_activity_url() == '{}/@{}'.format(
        settings.FUNKWHALE_URL, user.username)


def test_activity_user_serializer(factories):
    user = factories['users.User']()

    expected = {
        "type": "Person",
        "id": user.get_activity_url(),
        "name": user.username,
    }

    data = serializers.UserActivitySerializer(user).data

    assert data == expected
