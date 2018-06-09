from . import serializers
from . import tasks

ACTIVITY_TYPES = [
    "Accept",
    "Add",
    "Announce",
    "Arrive",
    "Block",
    "Create",
    "Delete",
    "Dislike",
    "Flag",
    "Follow",
    "Ignore",
    "Invite",
    "Join",
    "Leave",
    "Like",
    "Listen",
    "Move",
    "Offer",
    "Question",
    "Reject",
    "Read",
    "Remove",
    "TentativeReject",
    "TentativeAccept",
    "Travel",
    "Undo",
    "Update",
    "View",
]


OBJECT_TYPES = [
    "Article",
    "Audio",
    "Collection",
    "Document",
    "Event",
    "Image",
    "Note",
    "OrderedCollection",
    "Page",
    "Place",
    "Profile",
    "Relationship",
    "Tombstone",
    "Video",
] + ACTIVITY_TYPES


def deliver(activity, on_behalf_of, to=[]):
    return tasks.send.delay(activity=activity, actor_id=on_behalf_of.pk, to=to)


def accept_follow(follow):
    serializer = serializers.AcceptFollowSerializer(follow)
    return deliver(serializer.data, to=[follow.actor.url], on_behalf_of=follow.target)
