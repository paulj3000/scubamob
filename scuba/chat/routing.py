"""
WebSocket URL routing for the chat domain (docs/chat_dynamo.md Phase 6, §22).
"""
from django.urls import re_path

from scuba.chat.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'^ws/chat/$', ChatConsumer.as_asgi()),
]
