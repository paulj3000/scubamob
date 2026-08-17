"""
ParticipantRepository interface (docs/chat_dynamo.md §4.3, §13) and the
Django-ORM-backed implementation wrapping the Phase 1
ConversationParticipant SQL model.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional

from django.utils import timezone

from scuba.chat.models import ConversationParticipant


class ParticipantRepository(ABC):
    @abstractmethod
    def add_participant(self, conversation_id: str, user_id: str, *, role: str) -> Any:
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


class DjangoParticipantRepository(ParticipantRepository):
    """ Real implementation, backed by ConversationParticipant (Phase 1). """

    def add_participant(self, conversation_id: str, user_id: str, *, role: str):
        # (conversation, user) is uniquely constrained, so re-adding a
        # participant who previously left reactivates their existing row
        # (clears left_at) instead of raising IntegrityError on a second
        # insert -- the desired behavior for "rejoin".
        participant, _ = ConversationParticipant.objects.update_or_create(
            conversation_id=conversation_id, user_id=user_id,
            defaults={'role': role, 'left_at': None},
        )
        return participant

    def remove_participant(self, conversation_id: str, user_id: str) -> None:
        ConversationParticipant.objects.filter(
            conversation_id=conversation_id, user_id=user_id, left_at__isnull=True,
        ).update(left_at=timezone.now())

    def list_participants(self, conversation_id: str) -> list[Any]:
        return list(ConversationParticipant.objects.filter(
            conversation_id=conversation_id, left_at__isnull=True))

    def is_participant(self, conversation_id: str, user_id: str) -> bool:
        return ConversationParticipant.objects.filter(
            conversation_id=conversation_id, user_id=user_id, left_at__isnull=True,
        ).exists()

    def get_participant(self, conversation_id: str, user_id: str) -> Optional[Any]:
        return ConversationParticipant.objects.filter(
            conversation_id=conversation_id, user_id=user_id,
        ).first()

    def mark_read(self, conversation_id: str, user_id: str, *, last_read_message_id: str) -> None:
        ConversationParticipant.objects.filter(
            conversation_id=conversation_id, user_id=user_id,
        ).update(last_read_message_id=last_read_message_id, last_read_at=timezone.now())
