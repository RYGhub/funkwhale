import logging

from funkwhale_api.music import models as music_models

from . import activity
from . import actors
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
    follow = serializer.save(approved=True if autoapprove else None)
    if follow.approved:
        outbox.dispatch({"type": "Accept"}, context={"follow": follow})
    return {"object": follow.target, "related_object": follow}


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
    obj = serializer.validated_data["follow"]
    return {"object": obj, "related_object": obj.target}


@outbox.register({"type": "Accept"})
def outbox_accept(context):
    follow = context["follow"]
    if follow._meta.label == "federation.LibraryFollow":
        actor = follow.target.actor
    else:
        actor = follow.target
    payload = serializers.AcceptFollowSerializer(follow, context={"actor": actor}).data
    yield {
        "actor": actor,
        "type": "Accept",
        "payload": with_recipients(payload, to=[follow.actor]),
        "object": follow,
        "related_object": follow.target,
    }


@inbox.register({"type": "Undo", "object.type": "Follow"})
def inbox_undo_follow(payload, context):
    serializer = serializers.UndoFollowSerializer(data=payload, context=context)
    if not serializer.is_valid(raise_exception=context.get("raise_exception", False)):
        logger.debug(
            "Discarding invalid follow undo from %s: %s",
            context["actor"].fid,
            serializer.errors,
        )
        return

    serializer.save()


@outbox.register({"type": "Undo", "object.type": "Follow"})
def outbox_undo_follow(context):
    follow = context["follow"]
    actor = follow.actor
    if follow._meta.label == "federation.LibraryFollow":
        recipient = follow.target.actor
    else:
        recipient = follow.target
    payload = serializers.UndoFollowSerializer(follow, context={"actor": actor}).data
    yield {
        "actor": actor,
        "type": "Undo",
        "payload": with_recipients(payload, to=[recipient]),
        "object": follow,
        "related_object": follow.target,
    }


@outbox.register({"type": "Follow"})
def outbox_follow(context):
    follow = context["follow"]
    if follow._meta.label == "federation.LibraryFollow":
        target = follow.target.actor
    else:
        target = follow.target
    payload = serializers.FollowSerializer(follow, context={"actor": follow.actor}).data
    yield {
        "type": "Follow",
        "actor": follow.actor,
        "payload": with_recipients(payload, to=[target]),
        "object": follow.target,
        "related_object": follow,
    }


@outbox.register({"type": "Create", "object.type": "Audio"})
def outbox_create_audio(context):
    upload = context["upload"]
    serializer = serializers.ActivitySerializer(
        {
            "type": "Create",
            "actor": upload.library.actor.fid,
            "object": serializers.UploadSerializer(upload).data,
        }
    )
    yield {
        "type": "Create",
        "actor": upload.library.actor,
        "payload": with_recipients(
            serializer.data, to=[{"type": "followers", "target": upload.library}]
        ),
        "object": upload,
        "target": upload.library,
    }


@inbox.register({"type": "Create", "object.type": "Audio"})
def inbox_create_audio(payload, context):
    serializer = serializers.UploadSerializer(
        data=payload["object"],
        context={"activity": context.get("activity"), "actor": context["actor"]},
    )

    if not serializer.is_valid(raise_exception=context.get("raise_exception", False)):
        logger.warn("Discarding invalid audio create")
        return

    upload = serializer.save()

    return {"object": upload, "target": upload.library}


@inbox.register({"type": "Delete", "object.type": "Library"})
def inbox_delete_library(payload, context):
    actor = context["actor"]
    library_id = payload["object"].get("id")
    if not library_id:
        logger.debug("Discarding deletion of empty library")
        return

    try:
        library = actor.libraries.get(fid=library_id)
    except music_models.Library.DoesNotExist:
        logger.debug("Discarding deletion of unkwnown library %s", library_id)
        return

    library.delete()


@outbox.register({"type": "Delete", "object.type": "Library"})
def outbox_delete_library(context):
    library = context["library"]
    serializer = serializers.ActivitySerializer(
        {"type": "Delete", "object": {"type": "Library", "id": library.fid}}
    )
    yield {
        "type": "Delete",
        "actor": library.actor,
        "payload": with_recipients(
            serializer.data, to=[{"type": "followers", "target": library}]
        ),
    }


@outbox.register({"type": "Update", "object.type": "Library"})
def outbox_update_library(context):
    library = context["library"]
    serializer = serializers.ActivitySerializer(
        {"type": "Update", "object": serializers.LibrarySerializer(library).data}
    )

    yield {
        "type": "Update",
        "actor": library.actor,
        "payload": with_recipients(
            serializer.data, to=[{"type": "followers", "target": library}]
        ),
    }


@inbox.register({"type": "Update", "object.type": "Library"})
def inbox_update_library(payload, context):
    actor = context["actor"]
    library_id = payload["object"].get("id")
    if not library_id:
        logger.debug("Discarding deletion of empty library")
        return

    if not actor.libraries.filter(fid=library_id).exists():
        logger.debug("Discarding deletion of unkwnown library %s", library_id)
        return

    serializer = serializers.LibrarySerializer(data=payload["object"])
    if serializer.is_valid():
        serializer.save()
    else:
        logger.debug(
            "Discarding update of library %s because of payload errors: %s",
            library_id,
            serializer.errors,
        )


@inbox.register({"type": "Delete", "object.type": "Audio"})
def inbox_delete_audio(payload, context):
    actor = context["actor"]
    try:
        upload_fids = [i for i in payload["object"]["id"]]
    except TypeError:
        # we did not receive a list of Ids, so we can probably use the value directly
        upload_fids = [payload["object"]["id"]]

    candidates = music_models.Upload.objects.filter(
        library__actor=actor, fid__in=upload_fids
    )

    total = candidates.count()
    logger.info("Deleting %s uploads with ids %s", total, upload_fids)
    candidates.delete()


@outbox.register({"type": "Delete", "object.type": "Audio"})
def outbox_delete_audio(context):
    uploads = context["uploads"]
    library = uploads[0].library
    serializer = serializers.ActivitySerializer(
        {
            "type": "Delete",
            "object": {"type": "Audio", "id": [u.get_federation_id() for u in uploads]},
        }
    )
    yield {
        "type": "Delete",
        "actor": library.actor,
        "payload": with_recipients(
            serializer.data, to=[{"type": "followers", "target": library}]
        ),
    }


def handle_library_entry_update(payload, context, queryset, serializer_class):
    actor = context["actor"]
    obj_id = payload["object"].get("id")
    if not obj_id:
        logger.debug("Discarding update of empty obj")
        return

    try:
        obj = queryset.select_related("attributed_to").get(fid=obj_id)
    except queryset.model.DoesNotExist:
        logger.debug("Discarding update of unkwnown obj %s", obj_id)
        return
    if not actor.can_manage(obj):
        logger.debug(
            "Discarding unauthorize update of obj %s from %s", obj_id, actor.fid
        )
        return

    serializer = serializer_class(obj, data=payload["object"])
    if serializer.is_valid():
        serializer.save()
    else:
        logger.debug(
            "Discarding update of obj %s because of payload errors: %s",
            obj_id,
            serializer.errors,
        )


@inbox.register({"type": "Update", "object.type": "Track"})
def inbox_update_track(payload, context):
    return handle_library_entry_update(
        payload,
        context,
        queryset=music_models.Track.objects.all(),
        serializer_class=serializers.TrackSerializer,
    )


@inbox.register({"type": "Update", "object.type": "Artist"})
def inbox_update_artist(payload, context):
    return handle_library_entry_update(
        payload,
        context,
        queryset=music_models.Artist.objects.all(),
        serializer_class=serializers.ArtistSerializer,
    )


@inbox.register({"type": "Update", "object.type": "Album"})
def inbox_update_album(payload, context):
    return handle_library_entry_update(
        payload,
        context,
        queryset=music_models.Album.objects.all(),
        serializer_class=serializers.AlbumSerializer,
    )


@outbox.register({"type": "Update", "object.type": "Track"})
def outbox_update_track(context):
    track = context["track"]
    serializer = serializers.ActivitySerializer(
        {"type": "Update", "object": serializers.TrackSerializer(track).data}
    )

    yield {
        "type": "Update",
        "actor": actors.get_service_actor(),
        "payload": with_recipients(
            serializer.data,
            to=[activity.PUBLIC_ADDRESS, {"type": "instances_with_followers"}],
        ),
    }


@outbox.register({"type": "Update", "object.type": "Album"})
def outbox_update_album(context):
    album = context["album"]
    serializer = serializers.ActivitySerializer(
        {"type": "Update", "object": serializers.AlbumSerializer(album).data}
    )

    yield {
        "type": "Update",
        "actor": actors.get_service_actor(),
        "payload": with_recipients(
            serializer.data,
            to=[activity.PUBLIC_ADDRESS, {"type": "instances_with_followers"}],
        ),
    }


@outbox.register({"type": "Update", "object.type": "Artist"})
def outbox_update_artist(context):
    artist = context["artist"]
    serializer = serializers.ActivitySerializer(
        {"type": "Update", "object": serializers.ArtistSerializer(artist).data}
    )

    yield {
        "type": "Update",
        "actor": actors.get_service_actor(),
        "payload": with_recipients(
            serializer.data,
            to=[activity.PUBLIC_ADDRESS, {"type": "instances_with_followers"}],
        ),
    }
