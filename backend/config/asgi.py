"""
ASGI config for Coders War project.
Supports HTTP and WebSocket (Django Channels).
"""
import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

from apps.gamification.routing import websocket_urlpatterns       # noqa: E402
from apps.gamification.middleware import JWTAuthMiddlewareStack   # noqa: E402

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': JWTAuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
