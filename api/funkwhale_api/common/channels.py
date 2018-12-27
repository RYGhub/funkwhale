import json
import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.serializers.json import DjangoJSONEncoder

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()
group_add = async_to_sync(channel_layer.group_add)


def group_send(group, event):
    # we serialize the payload ourselves and deserialize it to ensure it
    # works with msgpack. This is dirty, but we'll find a better solution
    # later
    s = json.dumps(event, cls=DjangoJSONEncoder)
    event = json.loads(s)
    logger.debug(
        "[channels] Dispatching %s to group %s: %s",
        event["type"],
        group,
        {"type": event["data"]["type"]},
    )
    async_to_sync(channel_layer.group_send)(group, event)
