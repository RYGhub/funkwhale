from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import SessionMiddlewareStack
from django.conf.urls import url

from funkwhale_api.common.auth import TokenAuthMiddleware
from funkwhale_api.instance import consumers

application = ProtocolTypeRouter(
    {
        # Empty for now (http->django views is added by default)
        "websocket": SessionMiddlewareStack(
            TokenAuthMiddleware(
                URLRouter(
                    [url("^api/v1/activity$", consumers.InstanceActivityConsumer)]
                )
            )
        )
    }
)
