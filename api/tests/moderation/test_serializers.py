import json
import pytest
import urllib.parse

from django.core.serializers.json import DjangoJSONEncoder

from funkwhale_api.common import utils as common_utils
from funkwhale_api.federation import models as federation_models
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


@pytest.mark.parametrize(
    "factory_name, target_type, id_field, state_serializer",
    [
        ("music.Artist", "artist", "id", serializers.ArtistStateSerializer),
        ("music.Album", "album", "id", serializers.AlbumStateSerializer),
        ("music.Track", "track", "id", serializers.TrackStateSerializer),
        ("music.Library", "library", "uuid", serializers.LibraryStateSerializer),
        ("playlists.Playlist", "playlist", "id", serializers.PlaylistStateSerializer),
        (
            "federation.Actor",
            "account",
            "full_username",
            serializers.ActorStateSerializer,
        ),
    ],
)
def test_report_serializer_save(
    factory_name, target_type, id_field, state_serializer, factories, mocker, settings
):
    target = factories[factory_name]()
    target_owner = factories["federation.Actor"]()
    submitter = factories["federation.Actor"]()
    target_data = {"type": target_type, id_field: getattr(target, id_field)}
    payload = {
        "summary": "Report content",
        "type": "illegal_content",
        "target": target_data,
    }
    serializer = serializers.ReportSerializer(
        data=payload, context={"submitter": submitter}
    )
    get_target_owner = mocker.patch.object(
        serializers, "get_target_owner", return_value=target_owner
    )
    assert serializer.is_valid(raise_exception=True) is True

    report = serializer.save()

    expected_state = state_serializer(target).data
    expected_state["_target"] = json.loads(
        json.dumps(target_data, cls=DjangoJSONEncoder)
    )
    if hasattr(target, "fid"):
        expected_state["domain"] = urllib.parse.urlparse(target.fid).hostname
        expected_state["is_local"] = (
            expected_state["domain"] == settings.FEDERATION_HOSTNAME
        )
    else:
        expected_state["is_local"] = True
    assert report.target == target
    assert report.type == payload["type"]
    assert report.summary == payload["summary"]
    assert report.target_state == expected_state
    assert report.target_owner == target_owner
    get_target_owner.assert_called_once_with(target)


def test_report_serializer_save_anonymous(factories, mocker):
    target = factories["music.Artist"]()
    payload = {
        "summary": "Report content",
        "type": "illegal_content",
        "target": {"type": "artist", "id": target.pk},
        "submitter_email": "test@submitter.example",
    }
    serializer = serializers.ReportSerializer(data=payload)

    assert serializer.is_valid(raise_exception=True) is True

    report = serializer.save()

    assert report.target == target
    assert report.type == payload["type"]
    assert report.summary == payload["summary"]
    assert report.submitter_email == payload["submitter_email"]


@pytest.mark.parametrize(
    "factory_name, factory_kwargs, owner_field",
    [
        ("music.Artist", {"attributed": True}, "attributed_to"),
        ("music.Album", {"attributed": True}, "attributed_to"),
        ("music.Track", {"attributed": True}, "attributed_to"),
        ("music.Library", {}, "actor"),
        ("playlists.Playlist", {"user__with_actor": True}, "user.actor"),
        ("federation.Actor", {}, "self"),
    ],
)
def test_get_target_owner(factory_name, factory_kwargs, owner_field, factories):
    target = factories[factory_name](**factory_kwargs)
    if owner_field == "self":
        expected_owner = target
    else:
        expected_owner = common_utils.recursive_getattr(target, owner_field)

    assert isinstance(expected_owner, federation_models.Actor)
    assert serializers.get_target_owner(target) == expected_owner


def test_report_serializer_repr(factories, to_api_date):
    target = factories["music.Artist"]()
    report = factories["moderation.Report"](target=target)
    expected = {
        "uuid": str(report.uuid),
        "summary": report.summary,
        "type": report.type,
        "target": {"type": "artist", "id": target.pk},
        "creation_date": to_api_date(report.creation_date),
        "handled_date": None,
        "is_handled": False,
        "submitter_email": None,
    }
    serializer = serializers.ReportSerializer(report)
    assert serializer.data == expected


@pytest.mark.parametrize(
    "preference, context, payload, is_valid",
    [
        # anonymous reports not enabled for the category
        (
            ["illegal_content"],
            {},
            {"type": "other", "submitter_email": "hello@example.test"},
            False,
        ),
        # anonymous reports enabled for the category, but invalid email
        (["other"], {}, {"type": "other", "submitter_email": "hello@"}, False),
        # anonymous reports enabled for the category, no email
        (["other"], {}, {"type": "other"}, False),
        # anonymous reports enabled for the category, actor object is empty
        (["other"], {"submitter": None}, {"type": "other"}, False),
        # valid examples
        (
            ["other"],
            {},
            {"type": "other", "submitter_email": "hello@example.test"},
            True,
        ),
    ],
)
def test_report_serializer_save_unauthenticated_validation(
    preference, context, payload, is_valid, factories, preferences
):
    preferences["moderation__unauthenticated_report_types"] = preference
    target = factories["music.Artist"]()
    target_data = {"type": "artist", "id": target.id}
    payload["summary"] = "Test"
    payload["target"] = target_data
    serializer = serializers.ReportSerializer(data=payload, context=context)
    assert serializer.is_valid() is is_valid
