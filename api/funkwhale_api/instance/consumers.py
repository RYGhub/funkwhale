from funkwhale_api.common.consumers import JsonAuthConsumer


class InstanceActivityConsumer(JsonAuthConsumer):
    groups = ["instance_activity"]

    def event_send(self, message):
        self.send_json(message["data"])
