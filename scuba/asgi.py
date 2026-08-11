"""
ASGI config for scubamob project.

Serves regular Django views over ASGI/HTTP and the chat WebSocket route
(docs/chat_dynamo.md Phase 6, §22) side by side. get_asgi_application()
must run -- and django.setup() with it -- before anything below imports
chat.routing/consumers, since those touch Django models.
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scuba.settings')

django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack  # noqa: E402
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402

from scuba.chat.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
