from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from channels import auth
from funkwhale_api.common import channels


class JsonAuthConsumer(JsonWebsocketConsumer):
    def connect(self):
        if "user" not in self.scope:
            try:
                self.scope["user"] = async_to_sync(auth.get_user)(self.scope)
            except (ValueError, AssertionError, AttributeError, KeyError):
                return self.close()

        if self.scope["user"] and self.scope["user"].is_authenticated:
            return self.accept()
        else:
            return self.close()

    def accept(self):
        super().accept()
        for group in self.groups:
            channels.group_add(group, self.channel_name)
        for group in self.scope["user"].get_channels_groups():
            channels.group_add(group, self.channel_name)
