from funkwhale_api.radios import serializers


def test_create_tag_radio(factories):
    tag = factories["tags.Tag"]()

    data = {"radio_type": "tag", "related_object_id": tag.name}

    serializer = serializers.RadioSessionSerializer(data=data)
    assert serializer.is_valid(raise_exception=True) is True

    session = serializer.save()

    assert session.related_object_id == tag.pk
    assert session.related_object == tag


def test_create_artist_radio(factories):
    artist = factories["music.Artist"]()

    data = {"radio_type": "artist", "related_object_id": artist.pk}

    serializer = serializers.RadioSessionSerializer(data=data)
    assert serializer.is_valid(raise_exception=True) is True

    session = serializer.save()

    assert session.related_object_id == artist.pk
    assert session.related_object == artist


def test_tag_radio_repr(factories, to_api_date):
    tag = factories["tags.Tag"]()
    session = factories["radios.RadioSession"](related_object=tag, radio_type="tag")

    expected = {
        "id": session.pk,
        "radio_type": "tag",
        "custom_radio": None,
        "user": session.user.pk,
        "related_object_id": tag.name,
        "creation_date": to_api_date(session.creation_date),
    }
    assert serializers.RadioSessionSerializer(session).data == expected
