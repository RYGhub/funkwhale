from channels.generic.websocket import JsonWebsocketConsumer


class JsonAuthConsumer(JsonWebsocketConsumer):
    def connect(self):
        try:
            assert self.scope['user'].pk is not None
        except (AssertionError, AttributeError, KeyError):
            return self.close()

        return self.accept()
