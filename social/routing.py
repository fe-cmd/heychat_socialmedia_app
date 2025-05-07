from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
<<<<<<< HEAD
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path, re_path


from notification.consumers import NotificationConsumer

application = ProtocolTypeRouter({
	'websocket': AllowedHostsOriginValidator(
		AuthMiddlewareStack(
			URLRouter([
					path('', NotificationConsumer.as_asgi()),
			])
		)
	),
})
=======
import core.routing


application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            core.routing.websocket_urlpatterns
        )
    ),
})
>>>>>>> f98a03bb387ce676ea1fbb6a689c3a739dfe7f67
