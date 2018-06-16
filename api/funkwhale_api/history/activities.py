from funkwhale_api.activity import record
from funkwhale_api.common import channels

from . import serializers

record.registry.register_serializer(serializers.ListeningActivitySerializer)


@record.registry.register_consumer("history.Listening")
def broadcast_listening_to_instance_activity(data, obj):
    if obj.user.privacy_level not in ["instance", "everyone"]:
        return

    channels.group_send(
        "instance_activity", {"type": "event.send", "text": "", "data": data}
    )
