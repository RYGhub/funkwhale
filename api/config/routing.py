from django.conf.urls import url

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from funkwhale_api.common.auth import TokenAuthMiddleware
from funkwhale_api.instance import consumers


application = ProtocolTypeRouter({
    # Empty for now (http->django views is added by default)
    "websocket": TokenAuthMiddleware(
        URLRouter([
            url("^api/v1/instance/activity$",
                consumers.InstanceActivityConsumer),
        ])
    ),
})
