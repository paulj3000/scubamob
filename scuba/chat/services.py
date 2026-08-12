"""
Chat service layer (docs/chat_dynamo.md §16, Phase 3).

The rest of ScubaMob must call through these functions, never through a
repository or DynamoDB directly (§4.2). Every function defaults to the
real repositories (DynamoDB for messages, SQL for conversations/
participants) but accepts repository overrides so callers -- mainly
tests -- can substitute the Phase 0 in-memory fakes instead.
"""
import logging
from typing import Optional

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

from scuba.accounts.models import User
from scuba.chat.domain import Message, MessageType, generate_message_id, user_channel_group_name
from scuba.chat.events import ChatEvent, MessageEventType
from scuba.chat.exceptions import (
    BlockedUserError, ConversationNotFoundError, InsufficientRoleError, InvalidMessagePayloadError,
    InvalidSenderError, MessageNotFoundError, NotAConversationParticipantError, NotMessageOwnerError,
)
from scuba.chat.models import ConversationRole, ConversationType
from scuba.chat.repositories.conversation_repository import (
    ConversationRepository, DjangoConversationRepository,
)
from scuba.chat.repositories.message_repository import DynamoDBMessageRepository, MessageRepository
from scuba.chat.repositories.participant_repository import (
    DjangoParticipantRepository, ParticipantRepository,
)

_ADMIN_ROLES = (ConversationRole.ADMIN, ConversationRole.OWNER)

logger = logging.getLogger(__name__)


def _default_message_repository() -> MessageRepository:
    return DynamoDBMessageRepository()


def _default_conversation_repository() -> ConversationRepository:
    return DjangoConversationRepository()


def _default_participant_repository() -> ParticipantRepository:
    return DjangoParticipantRepository()


def _get_conversation_or_raise(conversation_repository, conversation_id):
    conversation = conversation_repository.get_conversation(conversation_id)
    if conversation is None:
        raise ConversationNotFoundError(f"no conversation {conversation_id}")
    return conversation


def _require_participant(participant_repository, conversation_id, user_id) -> None:
    if not participant_repository.is_participant(conversation_id, user_id):
        raise NotAConversationParticipantError(
            f"user {user_id} is not a current participant of conversation {conversation_id}")


def _require_role(participant_repository, conversation_id, user_id, allowed_roles):
    _require_participant(participant_repository, conversation_id, user_id)
    participant = participant_repository.get_participant(conversation_id, user_id)
    if participant.role not in allowed_roles:
        raise InsufficientRoleError(
            f"user {user_id} does not have sufficient role in conversation {conversation_id} "
            f"(has {participant.role}, needs one of {allowed_roles})")
    return participant


def _require_active_user(user_id: str) -> None:
    if not User.objects.filter(pk=user_id, is_active=True).exists():
        raise InvalidSenderError(f"{user_id} is not a valid active user")


def _validate_message_payload(body: str, message_type: str) -> None:
    if not body or not body.strip():
        raise InvalidMessagePayloadError("message body must not be empty")
    if message_type not in MessageType.ALL:
        raise InvalidMessagePayloadError(f"unknown message_type {message_type!r}")


def _check_direct_conversation_blocks(conversation, participant_repository, sender_id) -> None:
    """
    §16 step 3, scoped to DIRECT conversations for now. A fuller policy
    across group membership (reporting, spam throttling, etc.) is Phase 17
    (§36) -- not invented here ahead of schedule.
    """
    if conversation.conversation_type != ConversationType.DIRECT:
        return

    other_ids = {
        str(participant.user_id)
        for participant in participant_repository.list_participants(str(conversation.id))
    } - {str(sender_id)}
    if not other_ids:
        return

    sender = User.objects.filter(pk=sender_id).first()
    other = User.objects.filter(pk=next(iter(other_ids))).first()
    if sender is not None and other is not None and sender.is_blocked(other):
        raise BlockedUserError(
            f"user {sender_id} cannot message a blocked/blocking user "
            f"in conversation {conversation.id}")


def _message_to_event_payload(message: Message) -> dict:
    return {
        'message_id': message.message_id,
        'conversation_id': message.conversation_id,
        'sender_id': message.sender_id,
        'message_type': message.message_type,
        'body': message.body,
        'created_at': message.created_at.isoformat(),
        'client_message_id': message.client_message_id,
        'reply_to_message_id': message.reply_to_message_id,
        'entity_type': message.entity_type,
        'entity_id': message.entity_id,
    }


def _publish_event(
    event: ChatEvent, *, participant_repository: Optional[ParticipantRepository] = None,
) -> None:
    """
    Fans the event out to every current participant's WebSocket group
    (Phase 6, §22-24). The message is already durably persisted by the
    time this runs (§24: "Persist first, broadcast second.") -- a
    delivery failure here must never undo or fail the send itself, so
    channel-layer errors are logged, not raised.
    """
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return  # no CHANNEL_LAYERS configured (e.g. some test contexts) -- nothing to do

    participant_repository = participant_repository or _default_participant_repository()
    participants = participant_repository.list_participants(event.conversation_id)

    for participant in participants:
        try:
            async_to_sync(channel_layer.group_send)(
                user_channel_group_name(str(participant.user_id)),
                {'type': 'chat.event', 'payload': event.as_dict()},
            )
        except Exception:
            logger.exception(
                "Failed to publish %s for conversation %s to user %s",
                event.event, event.conversation_id, participant.user_id)


def _schedule_notifications(message: Message) -> None:
    """ No-op until Phase 10 adds the notification system (§29). """


def create_conversation(
    *, conversation_type: str, created_by: str, title: Optional[str] = None,
    conversation_repository: Optional[ConversationRepository] = None,
    participant_repository: Optional[ParticipantRepository] = None,
):
    if conversation_type == ConversationType.DIRECT:
        raise ValueError("use create_direct_conversation for DIRECT conversations")

    conversation_repository = conversation_repository or _default_conversation_repository()
    participant_repository = participant_repository or _default_participant_repository()

    conversation = conversation_repository.create_conversation(
        conversation_type=conversation_type, created_by=created_by, title=title)
    participant_repository.add_participant(
        str(conversation.id), created_by, role=ConversationRole.OWNER)
    return conversation


def create_direct_conversation(
    user_a: str, user_b: str,
    *, conversation_repository: Optional[ConversationRepository] = None,
):
    """ Wraps ConversationRepository.get_or_create_direct_conversation (§14). """
    conversation_repository = conversation_repository or _default_conversation_repository()
    return conversation_repository.get_or_create_direct_conversation(user_a, user_b)


def list_conversations(
    user_id: str, *, conversation_repository: Optional[ConversationRepository] = None,
):
    """ Every conversation the user currently belongs to (Phase 4, §19). """
    conversation_repository = conversation_repository or _default_conversation_repository()
    return conversation_repository.list_conversations_for_user(user_id)


def get_conversation(
    *, conversation_id: str, user_id: str,
    conversation_repository: Optional[ConversationRepository] = None,
    participant_repository: Optional[ParticipantRepository] = None,
):
    """ A single conversation -- only visible to its current participants. """
    conversation_repository = conversation_repository or _default_conversation_repository()
    participant_repository = participant_repository or _default_participant_repository()

    conversation = _get_conversation_or_raise(conversation_repository, conversation_id)
    _require_participant(participant_repository, conversation_id, user_id)
    return conversation


def update_conversation(
    *, conversation_id: str, actor_id: str, title: str,
    conversation_repository: Optional[ConversationRepository] = None,
    participant_repository: Optional[ParticipantRepository] = None,
):
    conversation_repository = conversation_repository or _default_conversation_repository()
    participant_repository = participant_repository or _default_participant_repository()

    _get_conversation_or_raise(conversation_repository, conversation_id)
    _require_role(participant_repository, conversation_id, actor_id, _ADMIN_ROLES)

    return conversation_repository.update_conversation(conversation_id, title=title)


def send_message(
    *, conversation_id: str, sender_id: str, body: str,
    client_message_id: Optional[str] = None,
    message_type: str = MessageType.TEXT,
    reply_to_message_id: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    message_repository: Optional[MessageRepository] = None,
    conversation_repository: Optional[ConversationRepository] = None,
    participant_repository: Optional[ParticipantRepository] = None,
) -> Message:
    """
    §16's ten-step flow: authenticate, check membership, check blocks,
    validate payload, generate the message id, persist to DynamoDB, update
    conversation metadata, publish the real-time event, schedule
    notifications, return the normalized message.
    """
    message_repository = message_repository or _default_message_repository()
    conversation_repository = conversation_repository or _default_conversation_repository()
    participant_repository = participant_repository or _default_participant_repository()

    _require_active_user(sender_id)                                                    # 1
    conversation = _get_conversation_or_raise(conversation_repository, conversation_id)  # 2
    _require_participant(participant_repository, conversation_id, sender_id)             # 2
    _check_direct_conversation_blocks(conversation, participant_repository, sender_id)   # 3
    _validate_message_payload(body, message_type)                                        # 4

    message = Message(
        message_id=generate_message_id(),                                               # 5
        conversation_id=conversation_id,
        sender_id=str(sender_id),
        message_type=message_type,
        body=body,
        created_at=timezone.now(),
        client_message_id=client_message_id,
        reply_to_message_id=reply_to_message_id,
        entity_type=entity_type,
        entity_id=entity_id,
    )
    message = message_repository.create_message(message)                                 # 6

    conversation_repository.update_last_message(                                         # 7
        conversation_id, message_id=message.message_id, sent_at=message.created_at)

    _publish_event(
        ChatEvent(
            event=MessageEventType.MESSAGE_CREATED,
            conversation_id=conversation_id,
            payload={'message': _message_to_event_payload(message)},
        ),
        participant_repository=participant_repository,
    )

    _schedule_notifications(message)                                                      # 9

    return message                                                                        # 10


def list_messages(
    *, conversation_id: str, user_id: str, limit: int = 50, cursor: Optional[str] = None,
    message_repository: Optional[MessageRepository] = None,
    participant_repository: Optional[ParticipantRepository] = None,
):
    """ Chronologically ordered, cursor-paginated (§10) -- only for current participants. """
    message_repository = message_repository or _default_message_repository()
    participant_repository = participant_repository or _default_participant_repository()

    _require_participant(participant_repository, conversation_id, user_id)
    return message_repository.list_messages(conversation_id, limit=limit, cursor=cursor)


def edit_message(
    *, conversation_id: str, message_id: str, editor_id: str, body: str,
    message_repository: Optional[MessageRepository] = None,
    participant_repository: Optional[ParticipantRepository] = None,
) -> Message:
    message_repository = message_repository or _default_message_repository()
    participant_repository = participant_repository or _default_participant_repository()

    _require_participant(participant_repository, conversation_id, editor_id)

    message = message_repository.get_message(conversation_id, message_id)
    if message is None:
        raise MessageNotFoundError(f"no message {message_id} in conversation {conversation_id}")
    if str(message.sender_id) != str(editor_id):
        raise NotMessageOwnerError(f"user {editor_id} did not author message {message_id}")

    _validate_message_payload(body, message.message_type)

    return message_repository.update_message(conversation_id, message_id, body=body)


def delete_message(
    *, conversation_id: str, message_id: str, deleter_id: str,
    message_repository: Optional[MessageRepository] = None,
    participant_repository: Optional[ParticipantRepository] = None,
) -> Message:
    """ Soft delete (§40) -- sets deleted_at, does not remove the item. """
    message_repository = message_repository or _default_message_repository()
    participant_repository = participant_repository or _default_participant_repository()

    _require_participant(participant_repository, conversation_id, deleter_id)

    message = message_repository.get_message(conversation_id, message_id)
    if message is None:
        raise MessageNotFoundError(f"no message {message_id} in conversation {conversation_id}")

    if str(message.sender_id) != str(deleter_id):
        # not the author -- only a conversation admin/owner may still delete it
        _require_role(participant_repository, conversation_id, deleter_id, _ADMIN_ROLES)

    return message_repository.soft_delete_message(conversation_id, message_id)


def mark_conversation_read(
    *, conversation_id: str, user_id: str, last_read_message_id: str,
    participant_repository: Optional[ParticipantRepository] = None,
) -> None:
    participant_repository = participant_repository or _default_participant_repository()
    _require_participant(participant_repository, conversation_id, user_id)
    participant_repository.mark_read(
        conversation_id, user_id, last_read_message_id=last_read_message_id)


def get_unread_conversation_ids(
    user_id: str, *, participant_repository: Optional[ParticipantRepository] = None,
) -> set[str]:
    """ Conversations with unread messages for this user (Phase 7, §25). """
    participant_repository = participant_repository or _default_participant_repository()
    return participant_repository.list_unread_conversation_ids(user_id)


def get_unread_count(
    user_id: str, *, participant_repository: Optional[ParticipantRepository] = None,
) -> int:
    """ Backs GET /api/chat/unread-count/ (Phase 7, §25). """
    return len(get_unread_conversation_ids(user_id, participant_repository=participant_repository))


def add_participant(
    *, conversation_id: str, user_id: str, actor_id: str, role: str = ConversationRole.MEMBER,
    conversation_repository: Optional[ConversationRepository] = None,
    participant_repository: Optional[ParticipantRepository] = None,
):
    conversation_repository = conversation_repository or _default_conversation_repository()
    participant_repository = participant_repository or _default_participant_repository()

    conversation = _get_conversation_or_raise(conversation_repository, conversation_id)
    if conversation.conversation_type == ConversationType.DIRECT:
        raise ValueError("cannot add participants to a DIRECT conversation")

    _require_role(participant_repository, conversation_id, actor_id, _ADMIN_ROLES)

    return participant_repository.add_participant(conversation_id, user_id, role=role)


def remove_participant(
    *, conversation_id: str, user_id: str, actor_id: str,
    participant_repository: Optional[ParticipantRepository] = None,
) -> None:
    participant_repository = participant_repository or _default_participant_repository()
    _require_role(participant_repository, conversation_id, actor_id, _ADMIN_ROLES)
    participant_repository.remove_participant(conversation_id, user_id)


def leave_conversation(
    *, conversation_id: str, user_id: str,
    participant_repository: Optional[ParticipantRepository] = None,
) -> None:
    participant_repository = participant_repository or _default_participant_repository()
    _require_participant(participant_repository, conversation_id, user_id)
    participant_repository.mark_left(conversation_id, user_id)


def archive_conversation(
    *, conversation_id: str, user_id: str, archived: bool = True,
    participant_repository: Optional[ParticipantRepository] = None,
) -> None:
    participant_repository = participant_repository or _default_participant_repository()
    _require_participant(participant_repository, conversation_id, user_id)
    participant_repository.set_archived(conversation_id, user_id, archived)


def mute_conversation(
    *, conversation_id: str, user_id: str, muted: bool = True,
    participant_repository: Optional[ParticipantRepository] = None,
) -> None:
    participant_repository = participant_repository or _default_participant_repository()
    _require_participant(participant_repository, conversation_id, user_id)
    participant_repository.set_muted(conversation_id, user_id, muted)
