"""
Chat domain objects (docs/chat_dynamo.md Phase 0: "Define message IDs",
"Define conversation IDs", §6 key structure, §18 idempotency).

Conversation ids are Django UUID primary keys (scuba.libs.models.uuidmodel.
UUIDModel, same convention every other ScubaMob app uses) once the Phase 1
SQL models exist -- nothing to define here yet.

Message ids have no ORM to assign them, since messages live in DynamoDB
(§15), so this module is their source of truth: application-generated,
not derived from the DynamoDB write itself (§7: "Use application-generated
unique IDs rather than relying entirely on timestamps for uniqueness.").
"""
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


class MessageType:
    """ Initial message payload kinds (docs/chat_dynamo.md §7, §31). """
    TEXT = 'TEXT'
    SYSTEM = 'SYSTEM'
    DIVE = 'DIVE'
    DIVE_PLAN = 'DIVE_PLAN'
    DIVE_SITE = 'DIVE_SITE'
    LOGBOOK_ENTRY = 'LOGBOOK_ENTRY'
    EQUIPMENT = 'EQUIPMENT'
    MARKETPLACE_ITEM = 'MARKETPLACE_ITEM'

    ALL = (TEXT, SYSTEM, DIVE, DIVE_PLAN, DIVE_SITE, LOGBOOK_ENTRY, EQUIPMENT, MARKETPLACE_ITEM)


def generate_message_id() -> str:
    """ A message id: a UUID4 with no dashes, matching UUIDModel.pk_as_str. """
    return uuid.uuid4().hex


def conversation_partition_key(conversation_id: str) -> str:
    """ DynamoDB PK for every item belonging to a conversation (§6). """
    return f"CONVERSATION#{conversation_id}"


def user_channel_group_name(user_id: str) -> str:
    """
    The channels-layer group a user's single authenticated WebSocket joins
    (§22). chat.services._publish_event fans a conversation event out to
    every current participant's group; chat.consumers.ChatConsumer joins
    its connecting user to exactly this group.
    """
    return f"chat_user_{user_id}"


def message_sort_key(created_at: datetime, message_id: str) -> str:
    """
    DynamoDB SK for a message (§6, §9): timestamp + message id, so that
    two messages created in the same millisecond still sort deterministically.
    """
    return f"MESSAGE#{created_at.isoformat()}#{message_id}"


@dataclass
class Message:
    """
    The domain object repositories and chat.services operate on -- not a
    Django model (messages aren't relational) and not a raw DynamoDB item
    (that shape is a MessageRepository implementation detail, §15).
    """
    message_id: str
    conversation_id: str
    sender_id: str
    message_type: str
    body: str
    created_at: datetime
    client_message_id: Optional[str] = None
    edited_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    reply_to_message_id: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
