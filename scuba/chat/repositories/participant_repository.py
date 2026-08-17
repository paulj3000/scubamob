"""
ParticipantRepository interface (docs/chat_dynamo.md §4.3, §13) and the
Phase 1 Django-ORM-backed implementation.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional

from django.db.models import F, Q
from django.utils import timezone

from scuba.chat.models import ConversationParticipant


class ParticipantRepository(ABC):
    @abstractmethod
    def add_participant(self, conversation_id: str, user_id: str, *, role: str = 'MEMBER') -> Any:
        ...

    @abstractmethod
    def remove_participant(self, conversation_id: str, user_id: str) -> None:
        ...

    @abstractmethod
    def list_participants(self, conversation_id: str) -> list[Any]:
        ...

    @abstractmethod
    def is_participant(self, conversation_id: str, user_id: str) -> bool:
        """ Used by chat.services to enforce §16 step 2 (membership check). """

    @abstractmethod
    def get_participant(self, conversation_id: str, user_id: str) -> Optional[Any]:
        ...

    @abstractmethod
    def mark_read(self, conversation_id: str, user_id: str, *, last_read_message_id: str) -> None:
        """ Updates last_read_message_id / last_read_at (§25). """

    @abstractmethod
    def list_unread_conversation_ids(self, user_id: str) -> set[str]:
        """
        Conversations where the user's last_read_message_id doesn't match
        the conversation's current last_message_id (§25-26). A pure SQL
        comparison of already-stored pointers -- never queries DynamoDB,
        per §26's "do not query every DynamoDB message every time an
        unread badge is rendered".
        """

    @abstractmethod
    def mark_left(self, conversation_id: str, user_id: str) -> None:
        """ Soft-leave: sets left_at (§13), unlike remove_participant's hard delete. """

    @abstractmethod
    def set_archived(self, conversation_id: str, user_id: str, archived: bool) -> None:
        ...

    @abstractmethod
    def set_muted(self, conversation_id: str, user_id: str, muted: bool) -> None:
        ...

    @abstractmethod
    def shares_conversation_with(self, user_id: str, other_user_id: str) -> bool:
        """
        True if both users are current (non-left) participants of at least
        one common conversation. Used by presence (§28, Phase 9) to scope
        who may look up whose presence -- the same privacy boundary
        everything else in chat already uses.
        """


class DjangoParticipantRepository(ParticipantRepository):
    """ Real implementation backed by the Phase 1 ConversationParticipant model. """

    def add_participant(
        self, conversation_id: str, user_id: str, *, role: str = 'MEMBER'
    ) -> ConversationParticipant:
        participant, _ = ConversationParticipant.objects.get_or_create(
            conversation_id=conversation_id, user_id=user_id, defaults={'role': role})
        return participant

    def remove_participant(self, conversation_id: str, user_id: str) -> None:
        ConversationParticipant.objects.filter(
            conversation_id=conversation_id, user_id=user_id).delete()

    def list_participants(self, conversation_id: str) -> list[ConversationParticipant]:
        return list(ConversationParticipant.objects.filter(conversation_id=conversation_id))

    def is_participant(self, conversation_id: str, user_id: str) -> bool:
        return ConversationParticipant.objects.filter(
            conversation_id=conversation_id, user_id=user_id, left_at__isnull=True).exists()

    def get_participant(self, conversation_id: str, user_id: str) -> Optional[ConversationParticipant]:
        return ConversationParticipant.objects.filter(
            conversation_id=conversation_id, user_id=user_id).first()

    def mark_read(self, conversation_id: str, user_id: str, *, last_read_message_id: str) -> None:
        ConversationParticipant.objects.filter(
            conversation_id=conversation_id, user_id=user_id
        ).update(last_read_message_id=last_read_message_id, last_read_at=timezone.now())

    def list_unread_conversation_ids(self, user_id: str) -> set[str]:
        unread = ConversationParticipant.objects.filter(
            user_id=user_id, left_at__isnull=True, conversation__last_message_id__isnull=False,
        ).filter(
            Q(last_read_message_id__isnull=True)
            | ~Q(last_read_message_id=F('conversation__last_message_id'))
        ).values_list('conversation_id', flat=True)
        return {str(conversation_id) for conversation_id in unread}

    def mark_left(self, conversation_id: str, user_id: str) -> None:
        ConversationParticipant.objects.filter(
            conversation_id=conversation_id, user_id=user_id
        ).update(left_at=timezone.now())

    def set_archived(self, conversation_id: str, user_id: str, archived: bool) -> None:
        ConversationParticipant.objects.filter(
            conversation_id=conversation_id, user_id=user_id
        ).update(archived=archived)

    def set_muted(self, conversation_id: str, user_id: str, muted: bool) -> None:
        ConversationParticipant.objects.filter(
            conversation_id=conversation_id, user_id=user_id
        ).update(muted=muted)

    def shares_conversation_with(self, user_id: str, other_user_id: str) -> bool:
        return ConversationParticipant.objects.filter(
            user_id=user_id, left_at__isnull=True,
            conversation__participants__user_id=other_user_id,
            conversation__participants__left_at__isnull=True,
        ).exists()
