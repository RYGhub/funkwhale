from funkwhale_api.common import models as common_models
from funkwhale_api.common import mutations
from funkwhale_api.common import serializers as common_serializers
from funkwhale_api.common import utils as common_utils

from funkwhale_api.federation import routes
from funkwhale_api.tags import models as tags_models
from funkwhale_api.tags import serializers as tags_serializers

from . import models

NOOP = object()


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

    def get_previous_state_handlers(self):
        handlers = super().get_previous_state_handlers()
        handlers["tags"] = lambda obj: list(
            sorted(obj.tagged_items.values_list("tag__name", flat=True))
        )
        return handlers

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", NOOP)
        r = super().update(instance, validated_data)
        if tags != NOOP:
            tags_models.set_tags(instance, *tags)
        return r


class DescriptionMutation(mutations.UpdateMutationSerializer):
    description = common_serializers.ContentSerializer()

    def get_previous_state_handlers(self):
        handlers = super().get_previous_state_handlers()
        handlers["description"] = (
            lambda obj: common_serializers.ContentSerializer(obj.description).data
            if obj.description_id
            else None
        )
        return handlers

    def update(self, instance, validated_data):
        description = validated_data.pop("description", NOOP)
        r = super().update(instance, validated_data)
        if description != NOOP:
            common_utils.attach_content(instance, "description", description)
        return r


class CoverMutation(mutations.UpdateMutationSerializer):
    cover = common_serializers.RelatedField(
        "uuid",
        queryset=common_models.Attachment.objects.all().local(),
        serializer=None,
    )

    def get_serialized_relations(self):
        serialized_relations = super().get_serialized_relations()
        serialized_relations["cover"] = "uuid"
        return serialized_relations

    def get_previous_state_handlers(self):
        handlers = super().get_previous_state_handlers()
        handlers["cover"] = (
            lambda obj: str(obj.attachment_cover.uuid) if obj.attachment_cover else None
        )
        return handlers

    def update(self, instance, validated_data):
        if "cover" in validated_data:
            validated_data["attachment_cover"] = validated_data.pop("cover")
        return super().update(instance, validated_data)

    def mutation_post_init(self, mutation):
        # link cover_attachment (if any) to mutation
        if "cover" not in mutation.payload:
            return
        try:
            attachment = common_models.Attachment.objects.get(
                uuid=mutation.payload["cover"]
            )
        except common_models.Attachment.DoesNotExist:
            return

        common_models.MutationAttachment.objects.create(
            attachment=attachment, mutation=mutation
        )


@mutations.registry.connect(
    "update",
    models.Track,
    perm_checkers={"suggest": can_suggest, "approve": can_approve},
)
class TrackMutationSerializer(CoverMutation, TagMutation, DescriptionMutation):
    class Meta:
        model = models.Track
        fields = [
            "license",
            "title",
            "position",
            "copyright",
            "tags",
            "description",
            "cover",
        ]

    def get_serialized_relations(self):
        serialized_relations = super().get_serialized_relations()
        serialized_relations["license"] = "code"
        return serialized_relations

    def post_apply(self, obj, validated_data):
        channel = obj.artist.get_channel()
        if channel:
            upload = channel.library.uploads.filter(track=obj).first()
            if upload:
                routes.outbox.dispatch(
                    {"type": "Update", "object": {"type": "Audio"}},
                    context={"upload": upload},
                )
        else:
            routes.outbox.dispatch(
                {"type": "Update", "object": {"type": "Track"}}, context={"track": obj}
            )


@mutations.registry.connect(
    "update",
    models.Artist,
    perm_checkers={"suggest": can_suggest, "approve": can_approve},
)
class ArtistMutationSerializer(CoverMutation, TagMutation, DescriptionMutation):
    class Meta:
        model = models.Artist
        fields = ["name", "tags", "description", "cover"]

    def post_apply(self, obj, validated_data):
        routes.outbox.dispatch(
            {"type": "Update", "object": {"type": "Artist"}}, context={"artist": obj}
        )


@mutations.registry.connect(
    "update",
    models.Album,
    perm_checkers={"suggest": can_suggest, "approve": can_approve},
)
class AlbumMutationSerializer(CoverMutation, TagMutation, DescriptionMutation):
    class Meta:
        model = models.Album
        fields = ["title", "release_date", "tags", "cover", "description"]

    def post_apply(self, obj, validated_data):
        routes.outbox.dispatch(
            {"type": "Update", "object": {"type": "Album"}}, context={"album": obj}
        )
