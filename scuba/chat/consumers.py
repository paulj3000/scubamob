"""
WebSocket consumer for real-time chat delivery (docs/chat_dynamo.md
Phase 6, §22-24).

A single authenticated WebSocket per client, not one per conversation
(§22): on connect, the consumer joins exactly one channel-layer group
keyed by the connecting user's id (scuba.chat.domain.
user_channel_group_name). chat.services._publish_event fans a
conversation event out to every current participant's group after the
message is already durably persisted in DynamoDB (§24: "Persist first,
broadcast second." -- this consumer only ever delivers events, it is
never the source of truth).
"""
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from scuba.chat.domain import user_channel_group_name


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user')
        if user is None or not user.is_authenticated:
            await self.close(code=4001)
            return

        self.group_name = user_channel_group_name(str(user.id))
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def chat_event(self, event):
        """ Handler for group_send(..., {'type': 'chat.event', 'payload': ...}). """
        await self.send_json(event['payload'])
