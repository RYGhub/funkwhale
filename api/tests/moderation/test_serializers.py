from funkwhale_api.moderation import serializers


def test_user_filter_serializer_repr(factories):
    artist = factories["music.Artist"]()
    content_filter = factories["moderation.UserFilter"](target_artist=artist)

    expected = {
        "uuid": str(content_filter.uuid),
        "target": {"type": "artist", "id": artist.pk, "name": artist.name},
        "creation_date": content_filter.creation_date.isoformat().replace(
            "+00:00", "Z"
        ),
    }

    serializer = serializers.UserFilterSerializer(content_filter)

    assert serializer.data == expected


def test_user_filter_serializer_save(factories):
    artist = factories["music.Artist"]()
    user = factories["users.User"]()
    data = {"target": {"type": "artist", "id": artist.pk}}

    serializer = serializers.UserFilterSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    content_filter = serializer.save(user=user)

    assert content_filter.target_artist == artist
