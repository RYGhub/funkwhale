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
        groups = self.scope["user"].get_channels_groups() + self.groups
        for group in groups:
            channels.group_add(group, self.channel_name)

    def disconnect(self, close_code):
        groups = self.scope["user"].get_channels_groups() + self.groups
        for group in groups:
            channels.group_discard(group, self.channel_name)
