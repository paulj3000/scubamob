"""
Chat service layer boundary (docs/chat_dynamo.md §16, Phase 3).

Phase 0 only defines the boundary the rest of ScubaMob is meant to call
through (§4.2: "They must not directly call DynamoDB.") -- the business
logic (permission checks, repository orchestration, idempotency, event
publishing) is Phase 3 and is not implemented here yet. Every function
below raises NotImplementedError until then.
"""
from typing import Optional

from scuba.chat.domain import Message


def create_conversation(*, conversation_type: str, created_by: str, title: Optional[str] = None):
    raise NotImplementedError("chat.services.create_conversation is Phase 3")


def create_direct_conversation(user_a: str, user_b: str):
    """ Wraps ConversationRepository.get_or_create_direct_conversation (§14). """
    raise NotImplementedError("chat.services.create_direct_conversation is Phase 3")


def send_message(
    *, conversation_id: str, sender_id: str, body: str,
    client_message_id: Optional[str] = None,
    message_type: str = 'TEXT',
    reply_to_message_id: Optional[str] = None,
) -> Message:
    """
    §16's ten-step flow: authenticate, check membership, check blocks,
    validate payload, generate the message id, persist to DynamoDB, update
    conversation metadata, publish the real-time event, schedule
    notifications, return the normalized message.
    """
    raise NotImplementedError("chat.services.send_message is Phase 3")


def edit_message(*, conversation_id: str, message_id: str, editor_id: str, body: str) -> Message:
    raise NotImplementedError("chat.services.edit_message is Phase 3")


def delete_message(*, conversation_id: str, message_id: str, deleter_id: str) -> Message:
    """ Soft delete (§40) -- sets deleted_at, does not remove the item. """
    raise NotImplementedError("chat.services.delete_message is Phase 3")


def mark_conversation_read(*, conversation_id: str, user_id: str, last_read_message_id: str) -> None:
    raise NotImplementedError("chat.services.mark_conversation_read is Phase 3")


def add_participant(*, conversation_id: str, user_id: str, actor_id: str, role: str = 'MEMBER'):
    raise NotImplementedError("chat.services.add_participant is Phase 3")


def remove_participant(*, conversation_id: str, user_id: str, actor_id: str) -> None:
    raise NotImplementedError("chat.services.remove_participant is Phase 3")


def leave_conversation(*, conversation_id: str, user_id: str) -> None:
    raise NotImplementedError("chat.services.leave_conversation is Phase 3")


def archive_conversation(*, conversation_id: str, user_id: str, archived: bool = True) -> None:
    raise NotImplementedError("chat.services.archive_conversation is Phase 3")


def mute_conversation(*, conversation_id: str, user_id: str, muted: bool = True) -> None:
    raise NotImplementedError("chat.services.mute_conversation is Phase 3")
