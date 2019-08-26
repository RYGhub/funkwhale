import persisting_theory

from rest_framework import serializers

from funkwhale_api.common import fields as common_fields
from funkwhale_api.common import preferences
from funkwhale_api.federation import models as federation_models
from funkwhale_api.federation import utils as federation_utils
from funkwhale_api.music import models as music_models
from funkwhale_api.playlists import models as playlists_models

from . import models


class FilteredArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = music_models.Artist
        fields = ["id", "name"]


class TargetSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["artist"])
    id = serializers.CharField()

    def to_representation(self, value):
        if value["type"] == "artist":
            data = FilteredArtistSerializer(value["obj"]).data
            data.update({"type": "artist"})
            return data

    def to_internal_value(self, value):
        if value["type"] == "artist":
            field = serializers.PrimaryKeyRelatedField(
                queryset=music_models.Artist.objects.all()
            )
        value["obj"] = field.to_internal_value(value["id"])
        return value


class UserFilterSerializer(serializers.ModelSerializer):
    target = TargetSerializer()

    class Meta:
        model = models.UserFilter
        fields = ["uuid", "target", "creation_date"]
        read_only_fields = ["uuid", "creation_date"]

    def validate(self, data):
        target = data.pop("target")
        if target["type"] == "artist":
            data["target_artist"] = target["obj"]

        return data


state_serializers = persisting_theory.Registry()


TAGS_FIELD = serializers.ListField(source="get_tags")


@state_serializers.register(name="music.Artist")
class ArtistStateSerializer(serializers.ModelSerializer):
    tags = TAGS_FIELD

    class Meta:
        model = music_models.Artist
        fields = ["id", "name", "mbid", "fid", "creation_date", "uuid", "tags"]


@state_serializers.register(name="music.Album")
class AlbumStateSerializer(serializers.ModelSerializer):
    tags = TAGS_FIELD
    artist = ArtistStateSerializer()

    class Meta:
        model = music_models.Album
        fields = [
            "id",
            "title",
            "mbid",
            "fid",
            "creation_date",
            "uuid",
            "artist",
            "release_date",
            "tags",
        ]


@state_serializers.register(name="music.Track")
class TrackStateSerializer(serializers.ModelSerializer):
    tags = TAGS_FIELD
    artist = ArtistStateSerializer()
    album = AlbumStateSerializer()

    class Meta:
        model = music_models.Track
        fields = [
            "id",
            "title",
            "mbid",
            "fid",
            "creation_date",
            "uuid",
            "artist",
            "album",
            "disc_number",
            "position",
            "license",
            "copyright",
            "tags",
        ]


@state_serializers.register(name="music.Library")
class LibraryStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = music_models.Library
        fields = ["id", "fid", "name", "description", "creation_date", "privacy_level"]


@state_serializers.register(name="playlists.Playlist")
class PlaylistStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = playlists_models.Playlist
        fields = ["id", "name", "creation_date", "privacy_level"]


@state_serializers.register(name="federation.Actor")
class ActorStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = federation_models.Actor
        fields = [
            "fid",
            "name",
            "preferred_username",
            "summary",
            "domain",
            "type",
            "creation_date",
        ]


def get_actor_query(attr, value):
    data = federation_utils.get_actor_data_from_username(value)
    return federation_utils.get_actor_from_username_data_query(None, data)


def get_target_owner(target):
    mapping = {
        music_models.Artist: lambda t: t.attributed_to,
        music_models.Album: lambda t: t.attributed_to,
        music_models.Track: lambda t: t.attributed_to,
        music_models.Library: lambda t: t.actor,
        playlists_models.Playlist: lambda t: t.user.actor,
        federation_models.Actor: lambda t: t,
    }

    return mapping[target.__class__](target)


TARGET_FIELD = common_fields.GenericRelation(
    {
        "artist": {"queryset": music_models.Artist.objects.all()},
        "album": {"queryset": music_models.Album.objects.all()},
        "track": {"queryset": music_models.Track.objects.all()},
        "library": {
            "queryset": music_models.Library.objects.all(),
            "id_attr": "uuid",
            "id_field": serializers.UUIDField(),
        },
        "playlist": {"queryset": playlists_models.Playlist.objects.all()},
        "account": {
            "queryset": federation_models.Actor.objects.all(),
            "id_attr": "full_username",
            "id_field": serializers.EmailField(),
            "get_query": get_actor_query,
        },
    }
)


class ReportSerializer(serializers.ModelSerializer):
    target = TARGET_FIELD

    class Meta:
        model = models.Report
        fields = [
            "uuid",
            "summary",
            "creation_date",
            "handled_date",
            "is_handled",
            "submitter_email",
            "target",
            "type",
        ]
        read_only_fields = ["uuid", "is_handled", "creation_date", "handled_date"]

    def validate(self, validated_data):
        validated_data = super().validate(validated_data)
        submitter = self.context.get("submitter")
        if submitter:
            # we have an authenticated actor so no need to check further
            return validated_data

        unauthenticated_report_types = preferences.get(
            "moderation__unauthenticated_report_types"
        )
        if validated_data["type"] not in unauthenticated_report_types:
            raise serializers.ValidationError(
                "You need an account to submit this report"
            )

        if not validated_data.get("submitter_email"):
            raise serializers.ValidationError(
                "You need to provide an email address to submit this report"
            )

        return validated_data

    def create(self, validated_data):
        target_state_serializer = state_serializers[
            validated_data["target"]._meta.label
        ]

        validated_data["target_state"] = target_state_serializer(
            validated_data["target"]
        ).data
        validated_data["target_owner"] = get_target_owner(validated_data["target"])
        return super().create(validated_data)
