import pytest

from funkwhale_api.federation import api_serializers
from funkwhale_api.federation import serializers


def test_library_serializer(factories):
    library = factories["music.Library"](uploads_count=5678)
    expected = {
        "fid": library.fid,
        "uuid": str(library.uuid),
        "actor": serializers.APIActorSerializer(library.actor).data,
        "name": library.name,
        "description": library.description,
        "creation_date": library.creation_date.isoformat().split("+")[0] + "Z",
        "uploads_count": library.uploads_count,
        "privacy_level": library.privacy_level,
        "follow": None,
        "latest_scan": None,
    }

    serializer = api_serializers.LibrarySerializer(library)

    assert serializer.data == expected


def test_library_serializer_latest_scan(factories):
    library = factories["music.Library"](uploads_count=5678)
    scan = factories["music.LibraryScan"](library=library)
    setattr(library, "latest_scans", [scan])
    expected = api_serializers.LibraryScanSerializer(scan).data
    serializer = api_serializers.LibrarySerializer(library)

    assert serializer.data["latest_scan"] == expected


def test_library_serializer_with_follow(factories):
    library = factories["music.Library"](uploads_count=5678)
    follow = factories["federation.LibraryFollow"](target=library)

    setattr(library, "_follows", [follow])
    expected = {
        "fid": library.fid,
        "uuid": str(library.uuid),
        "actor": serializers.APIActorSerializer(library.actor).data,
        "name": library.name,
        "description": library.description,
        "creation_date": library.creation_date.isoformat().split("+")[0] + "Z",
        "uploads_count": library.uploads_count,
        "privacy_level": library.privacy_level,
        "follow": api_serializers.NestedLibraryFollowSerializer(follow).data,
        "latest_scan": None,
    }

    serializer = api_serializers.LibrarySerializer(library)

    assert serializer.data == expected


def test_library_follow_serializer_validates_existing_follow(factories):
    follow = factories["federation.LibraryFollow"]()
    serializer = api_serializers.LibraryFollowSerializer(
        data={"target": follow.target.uuid}, context={"actor": follow.actor}
    )

    assert serializer.is_valid() is False
    assert "target" in serializer.errors


def test_library_follow_serializer_do_not_allow_own_library(factories):
    actor = factories["federation.Actor"]()
    library = factories["music.Library"](actor=actor)
    serializer = api_serializers.LibraryFollowSerializer(context={"actor": actor})

    with pytest.raises(api_serializers.serializers.ValidationError) as e:
        serializer.validate_target(library)
    assert "own library" in str(e)


def test_manage_upload_action_read(factories):
    ii = factories["federation.InboxItem"]()
    s = api_serializers.InboxItemActionSerializer(queryset=None)

    s.handle_read(ii.__class__.objects.all())

    assert ii.__class__.objects.filter(is_read=False).count() == 0
