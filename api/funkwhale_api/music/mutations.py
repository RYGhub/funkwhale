from funkwhale_api.common import mutations
from funkwhale_api.federation import routes

from . import models


def can_suggest(obj, actor):
    return obj.is_local


def can_approve(obj, actor):
    return obj.is_local and actor.user and actor.user.get_permissions()["library"]


@mutations.registry.connect(
    "update",
    models.Track,
    perm_checkers={"suggest": can_suggest, "approve": can_approve},
)
class TrackMutationSerializer(mutations.UpdateMutationSerializer):
    serialized_relations = {"license": "code"}

    class Meta:
        model = models.Track
        fields = ["license", "title", "position", "copyright"]

    def post_apply(self, obj, validated_data):
        routes.outbox.dispatch(
            {"type": "Update", "object": {"type": "Track"}}, context={"track": obj}
        )


@mutations.registry.connect(
    "update",
    models.Artist,
    perm_checkers={"suggest": can_suggest, "approve": can_approve},
)
class ArtistMutationSerializer(mutations.UpdateMutationSerializer):
    class Meta:
        model = models.Artist
        fields = ["name"]

    def post_apply(self, obj, validated_data):
        routes.outbox.dispatch(
            {"type": "Update", "object": {"type": "Artist"}}, context={"artist": obj}
        )


@mutations.registry.connect(
    "update",
    models.Album,
    perm_checkers={"suggest": can_suggest, "approve": can_approve},
)
class AlbumMutationSerializer(mutations.UpdateMutationSerializer):
    class Meta:
        model = models.Album
        fields = ["title", "release_date"]

    def post_apply(self, obj, validated_data):
        routes.outbox.dispatch(
            {"type": "Update", "object": {"type": "Album"}}, context={"album": obj}
        )
