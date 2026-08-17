"""
Chat domain objects (docs/chat_dynamo.md Phase 0: "Define message IDs",
"Define conversation IDs", §6 key structure, §18 idempotency).

Conversation ids are Django UUID primary keys (scuba.libs.models.uuidmodel.
UUIDModel, same convention every other ScubaMob app uses) -- see
scuba.chat.models.Conversation (Phase 1). Nothing to define here for them.

Message ids have no ORM to assign them, since messages live in DynamoDB
(§15), so this module is their source of truth: application-generated,
not derived from the DynamoDB write itself (§7: "Use application-generated
unique IDs rather than relying entirely on timestamps for uniqueness.").
"""
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


class PresenceState:
    """ The three presence states (docs/chat_dynamo.md §28, Phase 9). """
    ONLINE = 'ONLINE'
    RECENTLY_ACTIVE = 'RECENTLY_ACTIVE'
    OFFLINE = 'OFFLINE'

    ALL = (ONLINE, RECENTLY_ACTIVE, OFFLINE)


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


class AttachmentType:
    """
    Binary attachment kinds (docs/chat_dynamo.md §30, Phase 11). Scoped to
    real uploaded files only -- dive logs/plans/sites/equipment are already
    covered by Message.entity_type/entity_id (MessageType.DIVE_PLAN etc.,
    designed in Phase 0/1) and are not duplicated here.
    """
    IMAGE = 'IMAGE'
    DOCUMENT = 'DOCUMENT'

    ALL = (IMAGE, DOCUMENT)


def generate_message_id() -> str:
    """ A message id: a UUID4 with no dashes, matching UUIDModel.pk_as_str. """
    return uuid.uuid4().hex


def generate_attachment_id() -> str:
    """ An attachment id: same shape as a message id (§30). """
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


def attachment_sort_key(message_id: str, attachment_id: str) -> str:
    """
    DynamoDB SK for an attachment (§30): folds in the owning message id so
    every attachment of a message sorts together under the ATTACHMENT#
    prefix, mirroring MESSAGE# (§6).
    """
    return f"ATTACHMENT#{message_id}#{attachment_id}"


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


@dataclass
class Attachment:
    """
    A binary file attached to a message (§30) -- represented separately
    from Message, matching MessageAttachment in the doc's example schema.
    Not a Django model (attachments live in DynamoDB, §5) and not a raw
    DynamoDB item (that shape is an AttachmentRepository implementation
    detail). s3_key is a reference into CHAT_ATTACHMENT_BUCKET, never the
    binary content itself.
    """
    attachment_id: str
    conversation_id: str
    message_id: str
    attachment_type: str
    s3_key: str
    content_type: str
    size: int
    created_at: datetime
    original_filename: Optional[str] = None
