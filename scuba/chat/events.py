"""
Real-time event schema for the chat domain (docs/chat_dynamo.md §22/23/26).

Defined in Phase 0 so the service layer and, later, the Channels consumers
(Phase 6) agree on event names and payload shape up front. Nothing here
sends anything yet -- WebSocket delivery is Phase 6.
"""
from dataclasses import dataclass, field
from typing import Any


class MessageEventType:
    """ Initial WebSocket event types (docs/chat_dynamo.md §23). """
    MESSAGE_CREATED = 'message.created'
    MESSAGE_UPDATED = 'message.updated'
    MESSAGE_DELETED = 'message.deleted'
    CONVERSATION_UPDATED = 'conversation.updated'
    TYPING_STARTED = 'typing.started'
    TYPING_STOPPED = 'typing.stopped'
    MESSAGE_READ = 'message.read'
    PARTICIPANT_JOINED = 'participant.joined'
    PARTICIPANT_LEFT = 'participant.left'


@dataclass(frozen=True)
class ChatEvent:
    """
    The envelope every chat WebSocket event shares (docs/chat_dynamo.md §26):

        {"event": "message.created", "conversation_id": "...", "message": {}}

    `payload` holds the event-specific body (a serialized message, a typing
    indicator, etc.) -- its shape depends on `event`.
    """
    event: str
    conversation_id: str
    payload: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            'event': self.event,
            'conversation_id': self.conversation_id,
            **self.payload,
        }
