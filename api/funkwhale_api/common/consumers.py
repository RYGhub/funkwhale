from channels.generic.websocket import JsonWebsocketConsumer

from funkwhale_api.common import channels


class JsonAuthConsumer(JsonWebsocketConsumer):
    def connect(self):
        try:
            assert self.scope["user"].pk is not None
        except (AssertionError, AttributeError, KeyError):
            return self.close()

        return self.accept()

    def accept(self):
        super().accept()
        for group in self.groups:
            channels.group_add(group, self.channel_name)
        for group in self.scope["user"].get_channels_groups():
            channels.group_add(group, self.channel_name)
