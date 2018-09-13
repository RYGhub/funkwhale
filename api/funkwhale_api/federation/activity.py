import uuid
import logging

from django.db import transaction, IntegrityError
from django.utils import timezone

from funkwhale_api.common import channels
from funkwhale_api.common import utils as funkwhale_utils

logger = logging.getLogger(__name__)
PUBLIC_ADDRESS = "https://www.w3.org/ns/activitystreams#Public"

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


BROADCAST_TO_USER_ACTIVITIES = ["Follow", "Accept"]


@transaction.atomic
def receive(activity, on_behalf_of):
    from . import models
    from . import serializers
    from . import tasks

    # we ensure the activity has the bare minimum structure before storing
    # it in our database
    serializer = serializers.BaseActivitySerializer(
        data=activity, context={"actor": on_behalf_of, "local_recipients": True}
    )
    serializer.is_valid(raise_exception=True)
    try:
        copy = serializer.save()
    except IntegrityError:
        logger.warning(
            "[federation] Discarding already elivered activity %s",
            serializer.validated_data.get("id"),
        )
        return
    # we create inbox items for further delivery
    items = [
        models.InboxItem(activity=copy, actor=r, type="to")
        for r in serializer.validated_data["recipients"]["to"]
        if hasattr(r, "fid")
    ]
    items += [
        models.InboxItem(activity=copy, actor=r, type="cc")
        for r in serializer.validated_data["recipients"]["cc"]
        if hasattr(r, "fid")
    ]
    models.InboxItem.objects.bulk_create(items)
    # at this point, we have the activity in database. Even if we crash, it's
    # okay, as we can retry later
    funkwhale_utils.on_commit(tasks.dispatch_inbox.delay, activity_id=copy.pk)
    return copy


class Router:
    def __init__(self):
        self.routes = []

    def connect(self, route, handler):
        self.routes.append((route, handler))

    def register(self, route):
        def decorator(handler):
            self.connect(route, handler)
            return handler

        return decorator


class InboxRouter(Router):
    @transaction.atomic
    def dispatch(self, payload, context):
        """
        Receives an Activity payload and some context and trigger our
        business logic
        """
        from . import api_serializers
        from . import models

        for route, handler in self.routes:
            if match_route(route, payload):
                r = handler(payload, context=context)
                activity_obj = context.get("activity")
                if activity_obj and r:
                    # handler returned additional data we can use
                    # to update the activity target
                    for key, value in r.items():
                        setattr(activity_obj, key, value)

                    update_fields = []
                    for k in r.keys():
                        if k in ["object", "target", "related_object"]:
                            update_fields += [
                                "{}_id".format(k),
                                "{}_content_type".format(k),
                            ]
                        else:
                            update_fields.append(k)
                    activity_obj.save(update_fields=update_fields)

                if payload["type"] not in BROADCAST_TO_USER_ACTIVITIES:
                    return

                inbox_items = context.get(
                    "inbox_items", models.InboxItem.objects.none()
                )
                for ii in inbox_items:
                    user = ii.actor.get_user()
                    if not user:
                        continue
                    group = "user.{}.inbox".format(user.pk)
                    channels.group_send(
                        group,
                        {
                            "type": "event.send",
                            "text": "",
                            "data": {
                                "type": "inbox.item_added",
                                "item": api_serializers.InboxItemSerializer(ii).data,
                            },
                        },
                    )
                inbox_items.update(is_delivered=True, last_delivery_date=timezone.now())
                return


class OutboxRouter(Router):
    @transaction.atomic
    def dispatch(self, routing, context):
        """
        Receives a routing payload and some business objects in the context
        and may yield data that should be persisted in the Activity model
        for further delivery.
        """
        from . import models
        from . import tasks

        for route, handler in self.routes:
            if match_route(route, routing):
                activities_data = []
                for e in handler(context):
                    # a route can yield zero, one or more activity payloads
                    if e:
                        activities_data.append(e)
                inbox_items_by_activity_uuid = {}
                prepared_activities = []
                for activity_data in activities_data:
                    to = activity_data["payload"].pop("to", [])
                    cc = activity_data["payload"].pop("cc", [])
                    a = models.Activity(**activity_data)
                    a.uuid = uuid.uuid4()
                    to_items, new_to = prepare_inbox_items(to, "to")
                    cc_items, new_cc = prepare_inbox_items(cc, "cc")
                    if not to_items and not cc_items:
                        continue
                    inbox_items_by_activity_uuid[str(a.uuid)] = to_items + cc_items
                    if new_to:
                        a.payload["to"] = new_to
                    if new_cc:
                        a.payload["cc"] = new_cc
                    prepared_activities.append(a)

                activities = models.Activity.objects.bulk_create(prepared_activities)

                final_inbox_items = []
                for a in activities:
                    try:
                        prepared_inbox_items = inbox_items_by_activity_uuid[str(a.uuid)]
                    except KeyError:
                        continue

                    for ii in prepared_inbox_items:
                        ii.activity = a
                        final_inbox_items.append(ii)

                # create all inbox items, in bulk
                models.InboxItem.objects.bulk_create(final_inbox_items)

                for a in activities:
                    funkwhale_utils.on_commit(
                        tasks.dispatch_outbox.delay, activity_id=a.pk
                    )
                return activities


def match_route(route, payload):
    for key, value in route.items():
        if payload.get(key) != value:
            return False

    return True


def prepare_inbox_items(recipient_list, type):
    from . import models

    items = []
    new_list = []  # we return a list of actors url instead

    for r in recipient_list:
        if r != PUBLIC_ADDRESS:
            item = models.InboxItem(actor=r, type=type)
            items.append(item)
            new_list.append(r.fid)
        else:
            new_list.append(r)

    return items, new_list
