from funkwhale_api.common.consumers import JsonAuthConsumer


class MyConsumer(JsonAuthConsumer):
    groups = ["broadcast"]

    def receive_json(self, payload):
        print(payload, self.scope["user"])
        # Called with either text_data or bytes_data for each frame
        # You can call:
        self.send_json({'test': 'me'})
        # Or, to send a binary frame:
        # self.send(bytes_data="{Hello} world!")
        # Want to force-close the connection? Call:
        # self.close()
        # # Or add a custom WebSocket error code!
        # self.close(code=4123)
