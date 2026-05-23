from django.urls import re_path
from .consumers import DuelConsumer

websocket_urlpatterns = [
    re_path(r'^ws/duel/(?P<room_id>[A-Z0-9]+)/$', DuelConsumer.as_asgi()),
]
