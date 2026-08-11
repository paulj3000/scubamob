"""
ParticipantRepository interface (docs/chat_dynamo.md §4.3, §13) and the
Phase 1 Django-ORM-backed implementation.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional

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
