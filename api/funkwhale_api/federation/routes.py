import logging

from . import activity
from . import serializers

logger = logging.getLogger(__name__)
inbox = activity.InboxRouter()
outbox = activity.OutboxRouter()


def with_recipients(payload, to=[], cc=[]):
    if to:
        payload["to"] = to
    if cc:
        payload["cc"] = cc
    return payload


@inbox.register({"type": "Follow"})
def inbox_follow(payload, context):
    context["recipient"] = [
        ii.actor for ii in context["inbox_items"] if ii.type == "to"
    ][0]
    serializer = serializers.FollowSerializer(data=payload, context=context)
    if not serializer.is_valid(raise_exception=context.get("raise_exception", False)):
        logger.debug(
            "Discarding invalid follow from {}: %s",
            context["actor"].fid,
            serializer.errors,
        )
        return

    autoapprove = serializer.validated_data["object"].should_autoapprove_follow(
        context["actor"]
    )
    follow = serializer.save(approved=autoapprove)

    if autoapprove:
        activity.accept_follow(follow)


@inbox.register({"type": "Accept"})
def inbox_accept(payload, context):
    context["recipient"] = [
        ii.actor for ii in context["inbox_items"] if ii.type == "to"
    ][0]
    serializer = serializers.AcceptFollowSerializer(data=payload, context=context)
    if not serializer.is_valid(raise_exception=context.get("raise_exception", False)):
        logger.debug(
            "Discarding invalid accept from {}: %s",
            context["actor"].fid,
            serializer.errors,
        )
        return

    serializer.save()


@outbox.register({"type": "Accept"})
def outbox_accept(context):
    follow = context["follow"]
    if follow._meta.label == "federation.LibraryFollow":
        actor = follow.target.actor
    else:
        actor = follow.target
    payload = serializers.AcceptFollowSerializer(follow, context={"actor": actor}).data
    yield {"actor": actor, "payload": with_recipients(payload, to=[follow.actor])}


@outbox.register({"type": "Follow"})
def outbox_follow(context):
    follow = context["follow"]
    if follow._meta.label == "federation.LibraryFollow":
        target = follow.target.actor
    else:
        target = follow.target
    payload = serializers.FollowSerializer(follow, context={"actor": follow.actor}).data
    yield {"actor": follow.actor, "payload": with_recipients(payload, to=[target])}
