"""
WebSocket consumer for real-time chat delivery (docs/chat_dynamo.md
Phase 6, §22-24), typing indicators (Phase 8, §27), and presence
(Phase 9, §28).

A single authenticated WebSocket per client, not one per conversation
(§22): on connect, the consumer joins exactly one channel-layer group
keyed by the connecting user's id (scuba.chat.domain.
user_channel_group_name). chat.services._publish_event fans a
conversation event out to every current participant's group after the
message is already durably persisted in DynamoDB (§24: "Persist first,
broadcast second." -- this consumer only ever delivers events, it is
never the source of truth).

Typing indicators are the one thing this consumer accepts *inbound* --
everything else (sending messages, marking read, etc.) goes through the
REST API (Phase 4), which already has its own validation/serializer
layer. Typing state is too ephemeral and high-frequency to justify a
REST round trip, and the WebSocket is already open.

Presence has no inbound message of its own -- connect/disconnect *is*
the signal (chat.services.mark_user_online/mark_user_offline), read back
later through GET /api/chat/presence/<user_id>/ (Phase 9 was scoped
query-only, no WebSocket presence broadcast -- see TASK_TRACKER.md).
"""
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from scuba.chat import services
from scuba.chat.domain import user_channel_group_name
from scuba.chat.events import MessageEventType
from scuba.chat.exceptions import ChatError

_INBOUND_TYPING_HANDLERS = {
    MessageEventType.TYPING_STARTED: services.start_typing,
    MessageEventType.TYPING_STOPPED: services.stop_typing,
}


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user')
        if user is None or not user.is_authenticated:
            await self.close(code=4001)
            return

        self.group_name = user_channel_group_name(str(user.id))
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await database_sync_to_async(services.mark_user_online)(user_id=str(user.id))

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            user = self.scope.get('user')
            await database_sync_to_async(services.mark_user_offline)(user_id=str(user.id))

    async def receive_json(self, content, **kwargs):
        """
        Malformed or unrecognized payloads are ignored rather than closing
        the socket -- a stray client bug shouldn't kill an otherwise-
        healthy real-time connection. Likewise a ChatError (e.g. the user
        left the conversation since the socket connected) is swallowed:
        there is no request/response channel here to report it on.
        """
        conversation_id = content.get('conversation_id')
        handler = _INBOUND_TYPING_HANDLERS.get(content.get('type'))
        if not conversation_id or handler is None:
            return

        user = self.scope.get('user')
        try:
            await database_sync_to_async(handler)(
                conversation_id=conversation_id, user_id=str(user.id))
        except ChatError:
            pass

    async def chat_event(self, event):
        """ Handler for group_send(..., {'type': 'chat.event', 'payload': ...}). """
        await self.send_json(event['payload'])
