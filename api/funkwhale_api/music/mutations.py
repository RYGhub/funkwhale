from funkwhale_api.common import mutations

from . import models


def can_suggest(obj, actor):
    return True


def can_approve(obj, actor):
    return actor.user and actor.user.get_permissions()["library"]


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
