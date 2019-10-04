from funkwhale_api.common import mutations
from funkwhale_api.federation import routes
from funkwhale_api.tags import models as tags_models
from funkwhale_api.tags import serializers as tags_serializers

from . import models


def can_suggest(obj, actor):
    return obj.is_local


def can_approve(obj, actor):
    if not obj.is_local or not actor.user:
        return False

    return (
        actor.id is not None and actor.id == obj.attributed_to_id
    ) or actor.user.get_permissions()["library"]


class TagMutation(mutations.UpdateMutationSerializer):
    tags = tags_serializers.TagsListField()
    previous_state_handlers = {
        "tags": lambda obj: list(
            sorted(obj.tagged_items.values_list("tag__name", flat=True))
        )
    }

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", [])
        r = super().update(instance, validated_data)
        tags_models.set_tags(instance, *tags)
        return r


@mutations.registry.connect(
    "update",
    models.Track,
    perm_checkers={"suggest": can_suggest, "approve": can_approve},
)
class TrackMutationSerializer(TagMutation):
    serialized_relations = {"license": "code"}

    class Meta:
        model = models.Track
        fields = ["license", "title", "position", "copyright", "tags"]

    def post_apply(self, obj, validated_data):
        routes.outbox.dispatch(
            {"type": "Update", "object": {"type": "Track"}}, context={"track": obj}
        )


@mutations.registry.connect(
    "update",
    models.Artist,
    perm_checkers={"suggest": can_suggest, "approve": can_approve},
)
class ArtistMutationSerializer(TagMutation):
    class Meta:
        model = models.Artist
        fields = ["name", "tags"]

    def post_apply(self, obj, validated_data):
        routes.outbox.dispatch(
            {"type": "Update", "object": {"type": "Artist"}}, context={"artist": obj}
        )


@mutations.registry.connect(
    "update",
    models.Album,
    perm_checkers={"suggest": can_suggest, "approve": can_approve},
)
class AlbumMutationSerializer(TagMutation):
    class Meta:
        model = models.Album
        fields = ["title", "release_date", "tags"]

    def post_apply(self, obj, validated_data):
        routes.outbox.dispatch(
            {"type": "Update", "object": {"type": "Album"}}, context={"album": obj}
        )
